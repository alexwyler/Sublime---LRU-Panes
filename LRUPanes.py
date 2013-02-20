import sublime, sublime_plugin
import time

view_to_edit_time = {}
ordered_views = []
next_view = None

def init_panes():
  global ordered_views
  global view_to_edit_time
  cur_time = time.time()
  for view in sublime.active_window().views():
    ordered_views.append(view)
    view_to_edit_time[get_view_hash(view)] = cur_time

  push_view_to_top(sublime.active_window().active_view());

def next_pane_relative(offset):
  global ordered_views
  if not len(ordered_views):
    return None

  view = sublime.active_window().active_view()
  if (not view) or (ordered_views_indexof(view) == None):
    view = ordered_views[0]

  next_index = (ordered_views_indexof(view) + offset)

  # circular queing is confusing, so dont
  if next_index != next_index % len(ordered_views):
    return

  next_pane = ordered_views[next_index]
  return next_pane

def push_view_to_top(view):
  global ordered_views
  global view_to_edit_time

  view_hash = get_view_hash(view)
  view_to_edit_time[view_hash] = time.time()

  if ordered_views_indexof(view) == None:
    ordered_views.insert(0, view)
  discard_duplicate_views()

  ordered_views = sorted(
    ordered_views, key=lambda view: -view_to_edit_time[get_view_hash(view)])

def discard_duplicate_views():
  global ordered_views
  i = 0
  seen_views = set([])
  while (i < len(ordered_views)):
    view = ordered_views[i]
    view_hash = get_view_hash(view)
    if view_hash in seen_views:
      ordered_views.remove(view)
    else:
      seen_views.add(view_hash)
      i += 1

def open_next_pane_relative(offset):
  next_pane = next_pane_relative(offset)
  if next_pane:
    global next_view
    next_view = next_pane
    sublime.active_window().focus_view(next_pane)

def ordered_views_indexof(view):
  for i in range(0, len(ordered_views) - 1):
    existing_view = ordered_views[i]
    if get_view_hash(view) == get_view_hash(existing_view):
      return i
  return None

def get_view_hash(view):
  if view:
    return str(view.file_name()) + str(view.name())

class PreviousPaneCommand(sublime_plugin.WindowCommand):
  def run(self):
    open_next_pane_relative(-1)

class NextPaneCommand(sublime_plugin.WindowCommand):
  def run(self):
    open_next_pane_relative(1)

class LRUPaneListener(sublime_plugin.EventListener):
  def on_activated(self, view):
    global next_view
    if get_view_hash(view) != get_view_hash(next_view):
      push_view_to_top(view)
    else:
      next_view = None

  def on_load(self, view):
    global next_view
    if get_view_hash(view) != get_view_hash(next_view):
      push_view_to_top(view)
    else:
      next_view = None

init_panes()
