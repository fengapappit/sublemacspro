import functools as fu
import sublime, sublime_plugin


class SbpRegisterStore:
	"""
	Base class to stroe data for the registers, could be a plain dict,
	but we make it more complicated by wrapping the dict :)
	"""
	registers = {}

	def get(self, key):
		if not key in self.registers:
			return ""
		else:
			return self.registers[key]

	def store(self, key, val):
		self.registers[key] = val

	def  __contains__(self, key):
		return key in self.registers

# Global variable to store data in the registers
sbp_registers = SbpRegisterStore()



class SbpRegisterStore(sublime_plugin.TextCommand):
	'''
	Emacs style command allowing to store a certain value
	inside a global register.
	'''
	panel = None

	def run(self, edit):
		self.panel = self.view.window().show_input_panel("Store into register:", "", \
			self.on_done, \
			self.on_change,\
			self.on_cancel)

	def on_done(self, register):
		pass

	def on_cancel(self):
		pass

	def on_change(self, register):

		if self.panel == None:
			return

		self.panel.window().run_command("hide_panel")

		sel = self.view.sel()
		if (sel is None) or len(sel) != 1:
			return

		# Get the region
		sbp_registers.store(register, self.view.substr(sel[0]))
		self.view.run_command("sbp_cancel_mark")


class SbpRegisterInsert(sublime_plugin.TextCommand):
	"""
	Simple command to insert the value stored in the register
	at the point that is currently active
	"""

	panel = None

	def run(self, edit):
		self.panel = self.view.window().show_input_panel("Insert from register:", "", \
			None, \
			fu.partial(self.insert, edit),\
			None)

	def insert(self, edit, register):
		if not self.panel:
			return
		
		self.panel.window().run_command("hide_panel")

		sel = self.view.sel()
		if (sel is None) or len(sel) != 1:
			return

		begin = sel[0].begin()
		if register in sbp_registers:

			cnt = sbp_registers.get(register)
			self.view.replace(edit, sel[0], cnt)

			sel.clear()
			self.view.sel().add(begin + len(cnt))



class SbpOpenLineCommand(sublime_plugin.TextCommand):
    '''
    Emacs-style 'open-line' command: Inserts a newline at the current
    cursor position, without moving the cursor like Sublime's insert
    command does.
    '''
    def run(self, edit):
        sel = self.view.sel()
        if (sel is None) or (len(sel) == 0):
            return

        point = sel[0].end()
        self.view.insert(edit, point, '\n')
        self.view.run_command('move', {'by': 'characters', 'forward': False})


class SbpRecenterInView(sublime_plugin.TextCommand):
    '''
    Reposition the view so that the line containing the cursor is at the
    center of the viewport, if possible. Unlike the corresponding Emacs
    command, recenter-top-bottom, this command does not cycle through
    scrolling positions. It always repositions the view the same way.

    This command is frequently bound to Ctrl-l.
    '''
    def run(self, edit):
        self.view.show_at_center(self.view.sel()[0])

class SbpRectangleDelete(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		sel = self.view.sel()[0]
		b_row, b_col = self.view.rowcol(sel.begin())
		e_row, e_col = self.view.rowcol(sel.end())

		# Create rectangle
		top = b_row
		left = min(b_col, e_col)

		bot = e_row
		right = max(b_col, e_col)
		
		# For each line in the region, replace the contents by what we
		# gathered from the overlay
		current_edit = self.view.begin_edit()
		for l in range(top, bot + 1):
			r = sublime.Region(self.view.text_point(l, left), self.view.text_point(l, right))
			if not r.empty():
				self.view.erase(current_edit, r)
				
		self.view.end_edit(edit)
		self.view.run_command("sbp_cancel_mark")


class SbpRectangleInsert(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		self.view.window().show_input_panel("Content:", "", fu.partial(self.replace, edit), None, None)

	def replace(self, edit, content):

		sel = self.view.sel()[0]
		b_row, b_col = self.view.rowcol(sel.begin())
		e_row, e_col = self.view.rowcol(sel.end())

		# Create rectangle
		top = b_row
		left = min(b_col, e_col)

		bot = e_row
		right = max(b_col, e_col)
		
		# For each line in the region, replace the contents by what we
		# gathered from the overlay
		current_edit = self.view.begin_edit()
		for l in range(top, bot + 1):
			r = sublime.Region(self.view.text_point(l, left), self.view.text_point(l, right))
			if not r.empty():
				self.view.erase(current_edit, r)
			
			self.view.insert(current_edit, self.view.text_point(l, left), content)
		self.view.end_edit(edit)
		self.view.run_command("sbp_cancel_mark")
		

