# Restore the historical T2 base

Download all thirteen parts listed in delivery/Native-Master-Parts.json, including their original filenames. Run `python source/restore-master.py /path/to/parts /path/to/Gullyverse-Rev15T2.blend --index delivery/Native-Master-Parts.json`. The helper verifies every part and the complete file before writing the final result. This restoration was actually tested.

Expected complete file: 214,265,912 bytes, SHA256 33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb. The source and restoration instructions are also included in the final Rev15T3 checkpoint. T2 remains the complete base dependency for T3; its visible pothole treatment is superseded.
