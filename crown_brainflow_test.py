import json
import os
import time

import keyboard
from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter


def main() -> None:
    # Experiment name (used in folder / file names)
    experiment_name = "test1"

    liar_enabled = False
    liar_timestamp = None  # epoch seconds when "l" was pressed

    # Callback when "l" key is pressed
    def mark_liar() -> None:
        nonlocal liar_enabled, liar_timestamp
        liar_enabled = True
        liar_timestamp = time.time()
        print(f'[liar] "l" pressed, liar_timestamp = {liar_timestamp}')

    # Enable detailed logging (useful for debugging connection issues)
    BoardShim.enable_dev_board_logger()

    # Input params for CROWN.
    # For Crown / Notion 1 / Notion 2, nothing special is required here.
    params = BrainFlowInputParams()

    # Neurosity Crown board_id
    board_id = BoardIds.CROWN_BOARD.value

    # Create Board object
    board = BoardShim(board_id, params)

    try:
        print("=== BrainFlow: Crown session prepare ===")
        board.prepare_session()

        # Start stream
        # Example: board.start_stream(45000, "")  # keep 45000 samples in buffer
        board.start_stream()
        print("=== Streaming started ===")
        print('  "l" : set liar_timestamp')
        print('  "s" : stop and save data')

        # Register "l" hotkey to mark liar_timestamp
        keyboard.add_hotkey("l", mark_liar)

        # Wait until "s" is pressed
        keyboard.wait("s")
        keyboard.clear_all_hotkeys()
        print('"s" pressed. Stopping measurement and saving files...')

        # Get all data from internal buffer (this also clears the buffer)
        data = board.get_board_data()

        print("=== Stopping stream & releasing session ===")
        board.stop_stream()
        board.release_session()

        print(f"Data shape (rows x cols): {data.shape}")

        eeg_channels = BoardShim.get_eeg_channels(board_id)
        print(f"EEG channel indices: {eeg_channels}")

        work_dir = os.getcwd()
        now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

        # Prepare directories
        base_dir = os.path.join(work_dir, "data", experiment_name)
        raw_dir = os.path.join(base_dir, "crown_raw")
        os.makedirs(raw_dir, exist_ok=True)

        crown_filename = f"crown_raw_{now}.csv"

        # Build JSON metadata
        json_data = {
            "experiment_name": experiment_name,
            "created_at": now,
            "crown_filename": crown_filename,
            "liar_enabled": liar_enabled,
            "liar_timestamp": liar_timestamp,
        }

        # Save JSON
        json_out_file = os.path.join(base_dir, f"{experiment_name}_{now}.json")
        with open(json_out_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Save CSV (can be loaded by Python / MATLAB / Excel, etc.)
        out_file = os.path.join(raw_dir, crown_filename)
        DataFilter.write_file(data, out_file, "w")  # use "a" to append
        print(f"Raw data saved to: {out_file}")
        print(f"Metadata saved to: {json_out_file}")

    except Exception as e:
        print("Error occurred:")
        print(e)
        # Ensure session is released so that next connection will not fail
        try:
            board.stop_stream()
        except Exception:
            pass
        try:
            board.release_session()
        except Exception:
            pass


if __name__ == "__main__":
    main()
