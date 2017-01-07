import wave
import io
import math
import mtparser
import json
import itertools
import struct
import equalloudness
import sys

fs = 44100 # samples/sec

tempo = 120 # beats/min

class MyMusicTextSemantics(object):
    """
    Custom semantics that represent an accidental as an integer (positive for
    sharps, negative for flats, and 0 for neutral), and represent a note as a
    dictionary in which 'type' is mapped to 'name', and 'value' is mapped to the
    midi value of the note.
    """
    def accidental(self, ast):
        if ast.type == 'sharp':
            # + number of sharps
            return len(ast.acc_arr)
        elif ast.type == 'flat':
            # - number of flats
            return -len(ast.acc_arr)
        elif ast.type == 'natural':
            return 0
    
    def note(self, ast):
        # how many notes above the next lower C is this note's letter
        letter_off = 'c d ef g a b'.index(ast.letter.lower())
        # how many octaves higher than the middle octave is the octave that contains this note
        octave_off = len(ast.upoctave) if ast.upoctave is not None else -len(ast.downoctave)-1
        
        return {'type': 'note', 'value': 60 + octave_off * 12 + letter_off + ast.acc}

def note_idx_to_freq(note_idx):
    """
    Converts the midi note number (as int) to a frequency (as float).
    """
    return 440 * math.pow(2, (note_idx - 69) / 12)

class SynthParams:
    def __init__(self):
        self.alpha = 0
        self.omega = 0
        
def ast_beat_to_samples(ast_beat, beat_samples, sp=SynthParams(), y2=0, y1=0, amp=0.01):
    if ast_beat['type'] == 'pair':
        for subbeat in ast_beat['subbeats']:
            for samp in ast_beat_to_samples(subbeat, beat_samples // 2, sp=sp, y2=y2, y1=y1):
                yield samp
                y2, y1 = y1, samp
    elif ast_beat['type'] == 'triplet':
        for subbeat in ast_beat['subbeats']:
            for samp in ast_beat_to_samples(subbeat, beat_samples // 3, sp=sp, y2=y2, y1=y1):
                yield samp
                y2, y1 = y1, samp
    elif ast_beat['type'] == 'harmony':
        for samp in (sum(samps) for samps in zip(*(ast_to_samples(melody) for melody in ast_beat['melodies']))):
            yield samp
    else:
        if ast_beat['type'] == 'note':
            # parameters for sinusoid
            sp.omega = 2 * math.pi * note_idx_to_freq(ast_beat['value']) / fs # angular frequency
            sp.alpha = 0.00005 # decay speed
        elif ast_beat['type'] == 'rest':
            sp.alpha = 0.001
            
        freq = fs * sp.omega / (2 * math.pi)
        
        # coefficients for difference equation
        a1 = math.exp(-sp.alpha) * math.sin(sp.omega)
        b1 = 2 * math.exp(-sp.alpha) * math.cos(sp.omega)
        b2 = - math.exp(-2 * sp.alpha)
        
        samples_completed = 0
        if ast_beat['type'] == 'note':
            # initial 2 samples
            samp0 = b1 * y1 + b2 * y2
            samp1 = a1 * amp * math.pow(10, (equalloudness.lookup(freq) - 40) / 20) + b1 * samp0 + b2 * y1
            yield samp0
            yield samp1
            y2, y1 = samp0, samp1
            samples_completed = 2
        
        for _ in range(samples_completed, beat_samples):
            samp = b1 * y1 + b2 * y2
            yield samp
            y2, y1 = y1, samp

def ast_to_samples(ast):
    """
    Creates a generator for the samples (as floats). The parameter is the ast
    of the musictext.
    """
    synthparams = SynthParams()
    y2, y1 = 0, 0
    for ast_beat in ast:
        # save previous two samples
        for samp in ast_beat_to_samples(ast_beat, int(fs/tempo*60), sp=synthparams, y2=y2, y1=y1):
            yield samp
            y2, y1 = y1, samp

def samples_to_wav(samples):
    """
    Convert the samples (as an iterable of floats) into wav format. The [-0.5,
    0.5] range is translated into the [-32768, 32767] range.
    """
    buf = io.BytesIO()
    w = wave.open(buf, 'w')
    w.setnchannels(1)
    w.setframerate(fs)
    w.setsampwidth(2)
    
    b = bytearray()
    for x in samples:
        i = int(x * (1 << 16))
        i = max(-(1 << 15), min((1 << 15) - 1, i)) # clipping
        packed = struct.pack('<h', i)
        b += packed
    
    w.writeframes(b)
    
    return buf.getvalue()

def musictext_to_wav(musictext):
    """
    Convert the musictext (given as a str) into wav format. The result is a str
    object containing the bytes of the wav.
    """
    # parse the musictext into an abstract syntax tree
    ast = mtparser.MusicTextParser().parse(musictext, rule_name='start', semantics=MyMusicTextSemantics())
    # get a generator that will generate samples for the wav
    samples_iter = ast_to_samples(ast)
    # convert the samples into wav format
    return samples_to_wav(samples_iter)

if __name__ == '__main__':
    sys.stdout.buffer.write(musictext_to_wav(sys.stdin.read()))