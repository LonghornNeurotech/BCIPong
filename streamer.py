# streamer.py

import os
import time
import copy
import h5py
import torch
import asyncio
from multiprocessing import Event

async def async_train():
    """
    Asynchronously trains the model.
    """
    from online_training.train import Train  # Import here to avoid circular imports
    model_trainer = Train()
    await asyncio.to_thread(model_trainer.train)

def stream_predictions(conn, model_stream, stop_event):
    """
    Stream predictions from the AI model and send them to the game.

    Args:
        conn (Connection): The connection object to send predictions to the game.
        model_stream (Stream): The Stream object for getting AI predictions.
        stop_event (Event): Event to signal when to stop the stream.
        train (bool): Flag indicating whether to train the model.
    """
    train=False
    print(f"Stream predictions process started. PID: {os.getpid()}")

    max_retries = 5
    retry_delay = 2
    indexes = {}
    data_dict = {}

    # Attempt to start the stream
    for attempt in range(max_retries):
        try:
            model_stream.begin_stream()
            print("Stream started successfully.")
            break
        except Exception as e:
            print(f"Error starting stream (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to start stream.")
                return

    prev_index = 0
    event_number = 0

    with torch.no_grad():
        while not stop_event.is_set() and not model_stream.stop:
            try:
                time.sleep(0.08)
                one_hot, index, temp = model_stream.get_output()
                data_dict[index] = temp

                # Send command to the game
                command = int(one_hot[1])  # 1 for left, 0 for right
                conn.send({'type': 'DATA', 'command': command, 'index': index})
                
                while conn.poll():
                    message = conn.recv()
                    if isinstance(message, dict) and 'type' in message:
                        if message['type'] == 'SET_MODE':
                            if message['mode'] == 'TRAIN':
                                train = True
                                print("Training mode activated in stream_predictions.")
                            elif message['mode'] == 'PLAY':
                                train = False
                                print("Playing mode activated in stream_predictions.")
                        elif message['type'] == 'FEEDBACK':
                            pred = message['pred']
                            correct = message['correct']
                            index = message['index']
                            done = message['done']
                            # Handle training feedback as before
                            if train:
                                if prev_index != index:
                                    indexes[int(copy.deepcopy(index))] = copy.deepcopy({
                                        'data': copy.deepcopy(data_dict[index]),
                                        'pred': copy.deepcopy(pred),
                                        'correct': copy.deepcopy(correct)
                                    })
                                    del data_dict[index]

                                prev_index = index

                                if done:
                                    print("Game ended. Saving predictions...")
                                    current_time = time.strftime("%m%d-%H%M%S")
                                    filename = f"{os.getcwd()}/data/predictions_{correct}_{current_time}.h5"
                                    with h5py.File(filename, "w") as f:
                                        for idx in indexes.keys():
                                            group = f.create_group(str(idx))
                                            group.create_dataset("data", data=indexes[int(idx)]['data'])
                                            group.attrs['predicted'] = indexes[int(idx)]['pred']
                                            group.attrs['correct'] = indexes[int(idx)]['correct']
                                    model_stream.save_preds(index, correct)
                                    event_number += 1
                                    indexes.clear()
                                    data_dict.clear()
                                    while conn.poll():
                                        conn.recv()
                                    if event_number % 4 == 0:
                                        model_stream.model.train()
                                        model_stream.model = None
                                        loop = asyncio.get_event_loop()
                                        loop.run_until_complete(async_train())
                                        print("Model retrained.")
                                        model_stream.reload_model()
                                        print("Model reloaded.")
                                    conn.send(True)

            except Exception as e:
                print(f"Error in stream_predictions: {e}")
                break

    print("Stream predictions process ending.")
    model_stream.stop = True