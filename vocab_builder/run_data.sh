# build vocabulary
python build_vocab.py \
--count_threshold=0 \
--vocab_path='sample.vocab' \
--manifest_paths 'manifest.csv'

if [ $? -ne 0 ]; then
    echo "Build vocabulary failed. Terminated."
    exit 1
fi
