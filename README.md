# kar-edit

Utilities to help edit Karaoke (.kar) files

## Karaoke lyrics editing

This project contains files that allow editing lyrics in Karaoke (MIDI) file. In order to create MIDI (.kar) file with edited lyrics, one must perform following steps:

### Dumping karaoke lyrics

- Open terminal window
- In terminal window type `midi-dump karaoke_input_file.kar > karfile.dump`

Once script finishes, in directory there will be following file:

- **karfile.dump** containing text representation of karaoke (MIDI) file

### Preparing lyrics for editing

In already opened terminal window type: `./getmidilyrics.py -i karfile.dump`

Once script finishes, there will be two new files in current directory:

- **karfile.lyr.txt** containing just lyrics that can be edited
- **karfile.mark.txt** which is original .dump file containing placeholders for edited lyrics

You can now open **karfile.lyr.txt** file with any text editor and edit lyrics divided in syllables. Be careful NOT to delete other strings such as "/" or any hash sequence (#XXX)! Save the file and exit text editor.

### Merging back edited lyrics

In already opened terminal window type: `./mergemidilyrics.py -i karfile.dump`

Once script finishes in current directory there will be another file:

- **karfile.edit.txt** containing original dump file, but with lyrics you edited in **karfile.lyr.txt**

### Converting dump file back to MIDI file

In already opened terminal window type: `./midiconvert.sh karfile.edit.txt`

This will produce karaoke (MIDI) file with edited lyrics named **karfile.edit.kar** . To test everything is OK, you can play it with e.g. **timidity** utility like this: `timidity karfile.edit.kar`. You should see lyrics with your changes.

However, this is only the first part of karaoke journey. File **karfile.edit.kar** is just an input for the second phase - creating kaaoke video file.
