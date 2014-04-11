import sublime
import sublime_plugin
import os
import os.path
import subprocess

class TortoiseGITCommand(sublime_plugin.WindowCommand):
	def run(self, cmd, paths=None, isHung=False):
		dir = self.getPath(paths)

		if not dir:
			return
			
		settings = sublime.load_settings('TortoiseGIT.sublime-settings')
		tortoiseproc_path = settings.get('tortoiseproc_path')

		if not os.path.isfile(tortoiseproc_path):
			sublime.error_message(''.join(['can\'t find TortoiseGitProc.exe,',
				' please config setting file', '\n   --sublime-TortoiseGIT']))
			raise

		proce = subprocess.Popen('"' + tortoiseproc_path + '"' + 
			' /command:' + cmd + ' /path:"%s"' % dir , stdout=subprocess.PIPE)

		# This is required, cause of ST must wait TortoiseGIT update then revert
		# the file. Otherwise the file reverting occur before SVN update, if the
		# file changed the file content in ST is older.
		if isHung:
			proce.communicate()

	def getPath(self, paths):
		path = None
		if paths:
			path = '*'.join(paths)
		else:
			view = sublime.active_window().active_view()
			path = view.file_name() if view else None

		return path


class MutatingTortoiseGITCommand(TortoiseGITCommand):
	def run(self, cmd, paths=None):
		TortoiseGITCommand.run(self, cmd, paths, True)
		
		self.view = sublime.active_window().active_view()
		row, col = self.view.rowcol(self.view.sel()[0].begin())
		self.lastLine = str(row + 1);
		sublime.set_timeout(self.revert, 100)

	def revert(self):
		self.view.run_command('revert')
		sublime.set_timeout(self.revertPoint, 600)

	def revertPoint(self):
		self.view.window().run_command('goto_line',{'line':self.lastLine})


class GitCloneCommand(MutatingTortoiseGITCommand):
	def run(self, paths=None):
		settings = sublime.load_settings('TortoiseGIT.sublime-settings')
		closeonend = ('3' if True == settings.get('autoCloseUpdateDialog') else '0')
		MutatingTortoiseGITCommand.run(self, 'clone /closeonend:' + closeonend, paths)


class GitCommitCommand(TortoiseGITCommand):
	def run(self, paths=None):
		TortoiseGITCommand.run(self, 'commit /closeonend:3', paths)

class GitCheckoutCommand(TortoiseGITCommand):
	def run(self, paths=None):
		TortoiseGITCommand.run(self, 'checkout /closeonend:3', paths)

class GitPushCommand(TortoiseGITCommand):
	def run(self, paths=None):
		TortoiseGITCommand.run(self, 'push /closeonend:3', paths)

class GitPullCommand(TortoiseGITCommand):
	def run(self, paths=None):
		TortoiseGITCommand.run(self, 'pull /closeonend:3', paths)


class GitRevertCommand(MutatingTortoiseGITCommand):
	def run(self, paths=None):
		MutatingTortoiseGITCommand.run(self, 'revert', paths)


class GitLogCommand(TortoiseGITCommand):
	def run(self, paths=None):
		TortoiseGITCommand.run(self, 'log', paths)


class GitDiffCommand(TortoiseGITCommand):
	def run(self, paths=None):
		TortoiseGITCommand.run(self, 'diff', paths)


class GitBlameCommand(TortoiseGITCommand):
	def run(self, paths=None):
		view = sublime.active_window().active_view()
		row = view.rowcol(view.sel()[0].begin())[0] + 1

		TortoiseGITCommand.run(self, 'blame /line:' + str(row), paths)

	def is_visible(self, paths=None):
		file = self.getPath(paths)
		return os.path.isfile(file) if file else False
