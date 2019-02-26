import os
import re
import shutil
import tempfile
import yaml

import fire


def _number_pages(pdf_file):
  cmd = "pdfinfo %s | grep 'Pages' | awk '{print $2}'" % pdf_file
  return int(os.popen(cmd).read().strip())


def _last_png(directory):
  numbers = set()
  for fname in os.listdir(directory):
    match = re.search(r'^(\d*)\.png$', fname)
    if match:
      numbers.add(int(match.groups()[0]))
  if numbers:
    return list(sorted(numbers))[-1]
  return 0


def _png_file_generator(new_directory, last_png):
  def _output_file_names():
    file_num = last_png 
    while True:
      file_num += 1
      yield os.path.join(new_directory, '%d.png' % file_num)
  gen = _output_file_names()
  def nextfile():
    return next(gen)
  return nextfile


class FileComponent(object):

  def mogrify(self, pdf_glob, spread):
    if spread == 'double':
      width = 850
    else:
      width = 1424
    command = ((
      'mogrify -verbose -density 500 -resize %d -format png -flatten '
      '-background white "%s"') % (width, pdf_glob))
    # print(command)
    os.system(command)

  def separate_pages(self, pdf_file, output_directory):
    for i in range(_number_pages(pdf_file)):
      command = (
          'pdftk "%s" cat %d output %s/%d.pdf' %
          (pdf_file, i + 1, output_directory, i + 1))
      # print(command)
      os.system(command)

  def montage(self, directory, new_directory):
    """Combines contiguous pages into a single .png."""
    all_pngs = []
    for fname in os.listdir(directory):
      match = re.search(r'^(\d*)\.png$', fname)
      if match:
        all_pngs.append(int(match.groups()[0]))

    page_numbers = sorted(all_pngs)
    if len(page_numbers) % 2:
      page_numbers.append(None)

    last_png = _last_png(new_directory)
    next_file = _png_file_generator(new_directory, last_png)

    for p1, p2 in zip(page_numbers[::2], page_numbers[1::2]):
      def _png_for(page_number):
        if page_number is None:
          return os.path.join(os.path.dirname(__file__), 'blank.png')
        return os.path.join(directory, '%d.png' % page_number)
      page1 = _png_for(p1)
      page2 = _png_for(p2)
      new_file = next_file()
      print('Montaging to ' + new_file)
      command = (
          'montage %s %s -border 2 -bordercolor black -geometry +0+0 %s' %
          (page1, page2, new_file))
      # print(command)
      os.system(command)

  def rename_pngs(self, source, dest):
    canvas = '/home/cory/projects/online_journal/tools/canvas.png'
    last_png = _last_png(dest)
    for fname in os.listdir(source):
      match = re.search(r'^(\d*)\.png$', fname)
      if match:
        new_fname = '%d.png' % (int(match.groups()[0]) + last_png)
        print('Writing to ' + new_fname)
        command = 'convert %s %s -geometry +139 -composite %s' % (
            canvas, os.path.join(source, fname), os.path.join(dest, new_fname))
        # print(command)
        os.system(command)

  def process(self, config_file, do_sort=True):
    with open(config_file, 'r') as inp:
      config = yaml.load(inp)

    output_directory = config['output_directory']
    try:
      os.makedirs(output_directory)
    except FileExistsError:
      pass

    inputs = config.get('inputs', [])
    if do_sort:
      inputs.sort(key=lambda x: x['file'])
    tempdirs = []
    try:
      for pdf in config.get('inputs', []):
        fname = pdf['file']
        spread = pdf['format']
        newdir = tempfile.mkdtemp()
        
        # Splits original PDF into single-page PDFs.
        self.separate_pages(fname, newdir)

        # Converts PDFs into PNGs.
        self.mogrify(
            os.path.join(newdir, '*.pdf'),
            spread=spread)

        # Moves PNGs to output directory, changing format if necessary.
        if spread == 'double':
          self.montage(newdir, output_directory)
        else:
          assert spread == 'single'
          self.rename_pngs(newdir, output_directory)

    finally:
      for tempdir in tempdirs:
        shutil.rmtree(tempdir)

    with open(os.path.join(output_directory, 'meta.yaml'), 'w') as outp:
      yaml.dump(
          {'title': config['title'], 'cover': config['cover']}, outp)


if __name__ == '__main__':
  fire.Fire(FileComponent)
