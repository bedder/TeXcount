import sublime, sublime_plugin
from subprocess import PIPE, Popen
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
else:
	_ST3 = True
	try:
		from LaTeXTools import getTeXRoot
	except:
		from TeXcount import getTeXRoot
from os.path import dirname
from platform import system

class TexcountCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		filename = getTeXRoot.get_tex_root(self.view)

		# Check a file is selected
		if filename == None:
			sublime.error_message("No file in focus")
			return

		# Get the directory for the root tex file to use as the cwd
		dir = dirname(filename)

		# Save if file has been edited since last save
		if (self.view.is_dirty()):
			if (sublime.ok_cancel_dialog("File has changes, save to run TeXcount","Save")):
				self.view.run_command('save')
			else:
				return

		# Cleanse name and make shell command
		filename = filename.replace(" ","\ ")
		cmd = "texcount -merge " + filename

		
		if system() == 'Windows':
			pass
		else:
			# MacTex fix
			cmd = "PATH=$PATH:/usr/texbin; " + cmd

		# Test to see if texcount is installed and in available PATH
		testcmdprocess = Popen("texcount", shell=True, stdout=PIPE, stderr=PIPE)
		testout, testerr = testcmdprocess.communicate()
		if (testout == ""):
			sublime.error_message("TeXcount not installed in PATH \nDownload from: http://app.uio.no/ifi/texcount/")
			return

		# Excecute texcount and collect output
		p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd=dir)
		out, err = p.communicate()

		# Display output
		out = out.strip()
		if (_ST3):
			outputpanel = self.view.window().create_output_panel("texcountoutput")
			outputpanel.set_read_only(False)
			outputpanel.run_command('erase_view')
			outputpanel.run_command('append', {'characters': out.decode()})
			outputpanel.set_read_only(True)
			sublime.active_window().run_command("show_panel", {"panel": "output.texcountoutput"})
		else:
			outputpanel = self.view.window().get_output_panel("texcountoutput")
			outputpanel.set_read_only(False)
			edit = outputpanel.begin_edit()
			outputpanel.insert(edit, outputpanel.size(), out)
			outputpanel.show(outputpanel.size())
			outputpanel.show(sublime.Region(0))
			outputpanel.end_edit(edit)
			outputpanel.set_read_only(True)
			sublime.active_window().run_command("show_panel", {"panel": "output.texcountoutput", "toggle": True})

		return