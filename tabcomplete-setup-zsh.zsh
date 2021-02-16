# 	VIM SETTINGS: {{{3
# 	VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
# 	vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
# 	vim: set foldlevel=2 foldcolumn=3: 
# 	}}}1
#	{{{2
nl=$'\n'; tab=$'\t';

#	If shtab is installed, and dtscan is installed, and user shell is zsh, then continue
if ! command -v shtab > /dev/null; then
	echo "error, shtab not found" > /dev/stderr
	exit 2
fi
if ! command -v dtscan > /dev/null; then
	echo "error, dtscan not found" > /dev/stderr
	exit 2
fi
if ! command -v dtrange > /dev/null; then
	echo "error, dtrange not found" > /dev/stderr
	exit 2
fi

if [[ $SHELL == ".*/zsh" ]]; then
	echo "error, not zsh" > /dev/stderr
	exit 2
fi

#	zsh site-functions, standard directory for completion scripts
path_sitefunctions="/usr/local/share/zsh/site-functions"

#	name of file is package name with leading '_' (as per zsh convention)
name_completefile_scan="_dtscan"
name_completefile_range="_dtrange"

#	create zsh completions and write to path_sitefunctions
echo "Create file$nl$tab$path_sitefunctions/$name_completefile_scan" > /dev/stderr
shtab dtscan.__main__._parser_cliscan --shell=zsh > "$path_sitefunctions/$name_completefile_scan" #2> /dev/null

echo "Create file$nl$tab$path_sitefunctions/$name_completefile_range" > /dev/stderr
shtab dtscan.__main__._parser_clirange --shell=zsh > "$path_sitefunctions/$name_completefile_range" #2> /dev/null

#	Add tab-completion for files/directories for given arguments, since shtab (currently) does not do so
#	Filepath completion for -I | --infile
#		append '_files' to completion line
sed -i 's/{-I,--infile}"\[Input file\]:infile:"/{-I,--infile}"\[Input file\]:infile:_files"/' "$path_sitefunctions/$name_completefile_scan" 
#	Dirpath completion for --dir
#		append '_dir_list' to completion line
sed -i 's/"--dir\[\]:dir:"/"--dir\[\]:dir:_dir_list"/' "$path_sitefunctions/$name_completefile_scan" 


#	}}}1

