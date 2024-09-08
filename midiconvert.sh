#!/usr/bin/env sh

SANEFILENAME=$(echo $1 | tr ' ' _)
if [ "$1" != "$SANEFILENAME" ]; then
    mv "$1" "$SANEFILENAME"
fi

OUTFILE=$(echo "$SANEFILENAME" | sed -e 's/\.edit\.txt/\.pl/' -)
trs=$(echo "$SANEFILENAME" | sed -e 's/\.edit\.txt/\.edit.kar/' -)

echo "#!/usr/bin/env perl" > "$OUTFILE"
echo "use MIDI;" >> "$OUTFILE"
echo -n "my \$opus = " >> "$OUTFILE"
cat "$SANEFILENAME" >> "$OUTFILE"
echo "\$opus->write_to_file('"$trs"');" >> "$OUTFILE"
chmod u+x "$OUTFILE"
./"$OUTFILE"
if [ $? == 0 ]; then
  echo "INFO: Translated/converted MIDI is in '$trs'"
fi
/bin/rm -f "${OUTFILE}"
