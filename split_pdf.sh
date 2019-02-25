if [[ ${1} == "" ]]; then
  echo "Usage: split_pdf.sh <original_file> <num_pages> <output_directory>"
  return 1
fi
if [[ ${2} == "" ]]; then
  echo "Usage: split_pdf.sh <original_file> <num_pages> <output_directory>"
  return 1
fi
if [[ ${3} == "" ]]; then
  echo "Usage: split_pdf.sh <original_file> <num_pages> <output_directory>"
  return 1
fi

FILENAME=${1}
LASTPAGE=${2}
OUTDIR=${3}

for i in $(eval echo {1..${LASTPAGE}}); do
  pdftk "${FILENAME}" cat ${i} output ${OUTDIR}/${i}.pdf
done
