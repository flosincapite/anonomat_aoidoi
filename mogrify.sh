if [[ ${1} == "" ]]; then
  echo "Usage: mogrify.sh <file_glob>"
  exit 1
fi

mogrify \
  -verbose -density 500 -resize 800 -format png -flatten -background white \
  "${1}"
