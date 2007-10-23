#!/bin/sh
""exec /usr/local/vim7/bin/vim -u NONE -i NONE --noplugin -e --cmd ":so $0"
" vim:ft=vim:
" -e で ex モードにすることで、エスケープシーケンスを排除してる。
"  完全じゃないっぽい?


function Out(out)
	silent exe "normal a" . a:out
endfunction

try
	set hidden
	set termencoding=utf-8
	set encoding=utf-8
	set fileencodings=utf-8
	set fileencoding=utf-8

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

	let flavour = fnamemodify($PATH_INFO, ":e")
	if flavour == ""
		let flavour = "html"
	endif

	call Template("head.".flavour, {"title": "This is Vim.", "home": $SCRIPT_NAME})

	function CompareByTime(a, b)
		let a = a:a["time"]
		let b = a:b["time"]
		return a == b ? 0 : a > b ? -1 : 1
	endfunction

	function FilteringByPathInfo(entries)
		let pathinfo = split($PATH_INFO, "/")
		if len(pathinfo) > 0
			if str2nr(pathinfo[0]) == 0
				let pathinfo[len(pathinfo)-1] = fnamemodify($PATH_INFO, ":t:r")
				call filter(a:entries, '!match(v:val["name"], "^'.$PATH_INFO.'")')
			else
				"call Inspect('strftime("%Y", v:val["time"]) == '.string(pathinfo[0]))
				call filter(a:entries, 'strftime("%Y", v:val["time"]) == '.string(pathinfo[0]))
				if len(pathinfo) > 1
					call filter(a:entries, 'strftime("%m", v:val["time"]) == '.string(pathinfo[1]))
					if len(pathinfo) > 2
						call filter(a:entries, 'strftime("%d", v:val["time"]) == '.string(pathinfo[2]))
					end
				endif
			endif
		endif
	endfunction

	let files = split(glob("data/**/*.txt"), "\n")
	let entries = sort(map(files, '{"path": v:val, "time": getftime(v:val)}'), "CompareByTime")
	for ent in entries
		let file = readfile(ent["path"])
		let ent["title"] = file[0]
		let ent["body"]  = join(file[1:], "\n")
		let ent["name"]  = substitute(ent["path"], '^data\|.[^.]*$', "", "g")
		let ent["date"]  = strftime("%Y-%m-%d %H:%M:%S", ent["time"])
		let ent["home"]  = $SCRIPT_NAME
		let ent["path"]  = join(split(ent["home"], "/")[0:-1], "/")
	endfor

	call FilteringByPathInfo(entries)

	for ent in entries
		call Template("story.".flavour, ent)
	endfor

	call Template("foot.".flavour, {"version": version})
catch /.*/
	call Out("Content-Type: text/plain; charset=UTF-8\n\n")
	call Out(v:exception . "\n")
	call Out(v:throwpoint)
endtry

" Output
silent exe "w " . tempname()
silent exe "!cat %"
"silent echo join(getline(1, line("$")), "\n")
q!
