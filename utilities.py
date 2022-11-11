import os
from argparse import ArgumentParser
import operator



class File:
    """File object that can store file attributes(file size, file path, etc).
    This has class dictionary that will store summary of all file types. """

    file_dic = {}

    def __init__(self, file):
        self._path, self._filename = os.path.split(file)
        self._file = file
        self._size = os.path.getsize(file)
        self._extension = os.path.splitext(self._filename)[1][1:]
        self.count_files()

    def get_file_extension(self):
        '''Since git have multiple dots(.) this function checks it.
        and returns the file extension.'''
        if self.file().count('.') > 1:
            file_extension = 'git'
            return file_extension
        else:
            return self._extension

    def path(self):
        return self._path
        
    def file(self):
        return self._file

    def size(self):
        return self._size

    def filename(self):
        return self._filename

    def count_files(self):
        '''Count files with the same extension, sum its size then store both 
        count and size in a list and store the list in a dictionary 
        with the key of file extension.'''
        if self._extension not in File.file_dic:
            File.file_dic[self._extension] = [1, self.size()]
        else:
            File.file_dic[self._extension][0] += 1
            File.file_dic[self._extension][1] += self.size()




def format_size(size):
    '''Format the different file sizes into B, KB, MB and GB.
    Returns the formatted size like '8.5 GB' and '5 MB'.'''
    size = remove_zfill(size)
    if len(size) <= 3:
        size = size + ' B'
        return size.rjust(9)
    elif len(size) <= 6:
        size = round(int(size)/1_000, 2)
        size = str(size) + ' KB'
        return size.rjust(9)
    elif len(size) <= 9:
        size = round(int(size)/1_000_000, 2)
        size = str(size) + ' MB'
        return size.rjust(9)
    else:
        size = round(int(size)/1_000_000_000, 2)
        size = str(size) + ' GB'
        return size.rjust(9)


def remove_zfill(size):
    '''Remove all the zeros added that were help for sorting.'''
    if not size.startswith('0'):
        return size
    for char in size:
        if len(size) == 1:
            return size
        if char == '0':
            return remove_zfill(size[1:])


def file_gen(folder_path):
    '''Generate all files complete with each path in the given folder and its subfolders.'''
    for path, _, files, in os.walk(folder_path):
        for file in files:
            file_ = os.path.join(path, file)
            if not os.path.isfile(file_):
                continue
            yield file_


def write_to_file(folder, all_files, out_file):
    '''Write to a text file the summary of all files present.'''
    if not out_file[-3:] == 'txt':
        out_file = out_file + '.txt'

    with open(os.path.join(folder, out_file), 'w', encoding='utf8') as text_file:
        text_file.write('List of all files inside folders and its subfolders in "{}".\n\n'.upper().format(folder))

        for size, file in all_files:
            size = format_size(size)
            line = '{} - {}\n'.format(size, file)
            text_file.write(line)
            
        summary = '*********** SUMMARY ***********'.center(53)
        text_file.write('\n\n' + summary + '\n\n')

        t_size = 'Total Size'.center(17).upper()
        n_files = 'Number of Files'.center(17).upper()
        file_ = 'File'.center(17).upper()
        text_file.write(t_size + '|' + n_files + '|' + file_ + '\n')

        file_dic = dict(sorted(File.file_dic.items(), key=operator.itemgetter(1), reverse=True))

        for file_type, value in file_dic.items():
            num, size = value
            size = format_size(str(size)).center(17)
            file_type = test_if_hash(file_type)
            file_type = file_type.center(17)
            num = str(num).center(17)
            text_file.write(size + '|' + num + '|' + file_type + '\n')


def test_if_hash(file_type):
    '''Test if if the seen file is a hash.'''
    if len(file_type) == 0:
        return 'hash'
    else:
        return file_type


def main(folder, file_ext, del_flag, org_flag, out_file):

    all_files = []

    for file in file_gen(folder):
        # print(file)
        file_obj = File(file)

        # Checks if file extension is given and then compares it with the searched file extension
        if file_ext and not file_obj._extension == file_ext:
            continue
        all_files.append((str(file_obj.size()).zfill(12), file_obj.file()))
        if del_flag:
            os.remove(file)

    if org_flag:
        all_files.sort(key=lambda x: x[1])
        write_to_file(folder, all_files, out_file)
    else:
        all_files.sort(reverse=True)
        write_to_file(folder, all_files, out_file)


if __name__ == '__main__':

    my_parser = ArgumentParser(prog='Search files',
                               usage='Search files in a given directory. May choose specific filetypes. utilities -path "D:\Documents" -ext pdf -o pdf.txt -org',
                               description='Command Line Application searches a given directory then list and ' \
                               'summarize and write on a text file.',)
    my_parser.add_argument('-path', type=str, 
                                   default=os.curdir,
                                   help='dir/folder to be search of files')
    my_parser.add_argument('-ext', '--file_extension', type=str,
                                                   default=None,
                                                   help='Optional file extension that will be search')
    my_parser.add_argument('-del', '--delete',
                                         action='store_true',
                                         help='Delete all files with the specified file extension')
    my_parser.add_argument('-out', '--output', type=str,
                                            default='output.txt',
                                            help= 'Output file where reports will be saved')
    my_parser.add_argument('-org', '--organize', action='store_true',
                                                 help= 'Organize files and put different files into each folders in the summary, default is organized by size.')
    args = my_parser.parse_args()

    main(args.path, args.file_extension, args.delete, args.organize, args.output)