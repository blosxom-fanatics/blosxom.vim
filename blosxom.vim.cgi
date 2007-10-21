#!/bin/sh
""exec /usr/local/vim7/bin/vim -u NONE -i NONE --noplugin -e --cmd ":so $0"
" vim:ft=vim:
" -e で ex モードにすることで、エスケープシーケンスを排除してる。
"  完全じゃないっぽい?


function Out(out)
	silent exe "normal a" . a:out
endfunction

call Out("Content-Type: text/html; charset=UTF-8\n\n")


set hidden

function Inspect(obj)
	call Out(string(a:obj) . "\n")
endfunction


function Template(filename, dict)
	let retv = join(readfile(a:filename), "\n")
	for key in keys(a:dict)
		silent let retv = substitute(retv, "#{".key."}", substitute(a:dict[key], '\', '\\', 'g'), "g")
	endfor
	call Out(retv)
endfunction

call Template("head.html", {"title": "This is Vim."})


function CompareByTime(a, b)
	let a = a:a["time"]
	let b = a:b["time"]
	return a == b ? 0 : a > b ? -1 : 1
endfunction

call Inspect($PATH_INFO)
call Out(strftime("%Y-%m-%d %H:%M:%S\n"))
let files = split(glob("data/**/*.txt"), "\n")
let entries = sort(map(files, '{"path": v:val, "time": getftime(v:val)}'), "CompareByTime")
for ent in entries
	let file = readfile(ent["path"])
	let ent["title"] = file[0]
	let ent["body"] = join(file[1:], "\n")
	let ent["name"] = substitute(ent["path"], '^data\|.[^.]*$', "", "")
	let ent["date"] = strftime("%Y-%m-%d %H:%M:%S", ent["time"])
	let ent["home"] = $SCRIPT_NAME ? $SCRIPT_NAME : ""
	let ent["path"] = join(split(ent["home"], "/")[0:-1], "/")
	" call Out(ent["title"] . " " . ent["path"] . "\n")
	call Template("story.html", ent)
endfor

call Template("foot.html", {"version": version})

" Output
silent exe "w " . tempname()
silent exe "!cat %"
q!
