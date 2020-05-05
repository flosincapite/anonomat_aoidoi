DIRECTORY=${1}
EXTENSION=${2:-docx}

find ${DIRECTORY} | grep "\.${EXTENSION}" | while read fname; do
    libreoffice --headless --convert-to html:HTML \
        --outdir `dirname "$fname"` "$fname"
done
