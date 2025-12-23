import pretty_midi # pip install pretty_midi
import imageio.v2 as imageio
from tqdm import tqdm
# this starts at 37 - so, the 0 index is pitch 37. 
# 37 is the midi representation of D flat below the bass clef staff. 
# This is the lowest note in the song.
pitches_to_slide_positions = [
    6, # Db2
    5, # D2
    3, # Eb2
    2, # E2
    6, # F2
    5, # Gb2
    4, # G2
    3, # Ab2
    2, # A2
    1, # Bb2
    7, # B2
    6, # C3
    5, # Db3
    4, # D3
    3, # Eb3
    2, # E3
    1, # F3
    5, # Gb3
    4, # G3
    3, # Ab3
    2, # A3
    1, # Bb3
    4, # B3
    3, # C4
    2, # Db4
    1, # D4
    3, # Eb4
    2, # E4
    1, # F4
    3, # Gb4
    2, # G4
    3, # Ab4
]

def pretty_midi_to_slide_position(midi_data):
    END_TIME = (midi_data.get_end_time() + 3) * 1000 # end of the last note, in milliseconds
    instrument = midi_data.instruments[0]

    notes_with_duplicates = []
    end_marker = END_TIME
    for note in reversed(instrument.notes):
        position = pitches_to_slide_positions[note.pitch - 37]

        # TODO handle adding extra notes here. We're gonna skip the hard part of calculating the time between the current note, the next note, and adding bonus "fake" notes between rn
        start_ms = note.start * 1000
        notes_with_duplicates.append({
            'position': position, 
            'start_ms': start_ms,
            'duration': end_marker - start_ms
        })

        end_marker = start_ms
    notes_with_duplicates.reverse()
    return notes_with_duplicates


def write_image(positions_with_times):
    # load in sets of 7-position images (each set of 7 in their own folder)
    num_picture_sets = 3 # TODO change this to the number of folders you have
    positions = [1, 2, 3, 4, 5, 6, 7]
    image_sets = []
    for set_num in range(1, num_picture_sets+1):
        set_folder = f"set_{set_num}"
        images = []
        for i in range(1, 8):
            filename = f"images/{set_folder}/{i}.png"
            images.append(imageio.imread(filename))
            #print(filename)
        image_sets.append(images)

    FPS = 3
    MAX_LENGTH = 1000/FPS

    # GIFs have centisecond resolution, not millisecond.
    # Most values are going to be rounded up at this tempo - 375ms is an 8th note.
    # We need to keep track of drift, rounding some values up and some down
    # positive rounding error means that the cumulative frame duration is longer than the real values; resultant video is too slow
    rounding_error_ms = 0
    def handle_centisecond_rounding_for_gif_format(ms_value):
        nonlocal rounding_error_ms
        rounded_to_cs = round(ms_value / 10) * 10
        rounding_error_ms += (rounded_to_cs - ms_value)
        if rounding_error_ms >= 10:
            rounding_error_ms -= 10
            rounded_to_cs -= 10
        elif rounding_error_ms <= -10:
            rounding_error_ms += 10
            rounded_to_cs += 10
        
        return rounded_to_cs



    positions_with_times_with_duplicates = []

    # this is way out here so that we don't always start every note with the first image set. We rotate through them
    current_set = 0

    for position in positions_with_times:
        remainingDuration = position["duration"]
        start_ms = position["start_ms"]

        debug_total_ms_written = 0

        # # HACK! we just want to try subdividing each note evenly into two. Set max length accordingly
        # MAX_LENGTH = (remainingDuration / 2)
        # #print(MAX_LENGTH)

        # HACK! we just want to try setting max length to an 8th note
        MAX_LENGTH = 375
        while remainingDuration > MAX_LENGTH:
            # insert new frame of max length
            new_frame_duration = handle_centisecond_rounding_for_gif_format(MAX_LENGTH)
            positions_with_times_with_duplicates.append({
                'position': position["position"], 
                'start_ms': start_ms,
                'duration': new_frame_duration
            })
            debug_total_ms_written += new_frame_duration
            start_ms += new_frame_duration

            # This is extremely counterintuitive (for my brain, at least). 
            # Let's say we want to display a 375ms note. We round up to 380. If we subtract the remaining duration by 380, we have -5ms remaining duration. 
            remainingDuration -= new_frame_duration
        if remainingDuration < 0:
            print("NEGATIVE DRIFT")
            print(remainingDuration)
        # insert the remaining length

        if (remainingDuration > 0):
            new_frame_duration = handle_centisecond_rounding_for_gif_format(remainingDuration)
            positions_with_times_with_duplicates.append({
                'position': position["position"], 
                'start_ms': start_ms,
                'duration': new_frame_duration
            })
            debug_total_ms_written += new_frame_duration

        #print(debug_total_ms_written - position["duration"])
    durations = []
    for position in positions_with_times_with_duplicates:
        #print(position)
        durations.append(position["duration"])

    
    with imageio.get_writer('output.gif', mode='I', duration=durations, disposal=2) as writer:
        for position in tqdm(positions_with_times_with_duplicates):




            writer.append_data(image_sets[current_set][position["position"]-1])

            current_set += 1

            if current_set == num_picture_sets:
                current_set = 0
            #print(position["position"])

        writer.close()
        

def main():
    midi_data = pretty_midi.PrettyMIDI('midi/tb1.mid')
    positions_with_times = pretty_midi_to_slide_position(midi_data)
    # print(positions_with_times)
    write_image(positions_with_times)





#https://github.com/craffel/pretty-midi
#https://imageio.readthedocs.io/en/stable/
#https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python


'''
Per part: 
Get a list of notes and durations. 
Produce a list of slide positions and durations. 

Loop through the list. Future: For each note longer than MAX_DURATION, replace the long note in-place with multiple shorter notes (with different images).
Associate each position with an image. Produce a list of images and durations.

Feed the list of images and durations into the GIF compiler. 
'''






if __name__ == "__main__":
    main()