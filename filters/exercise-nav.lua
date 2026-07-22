local nav_data = nil

local function get_nav_json_path()
  local project_dir = os.getenv("QUARTO_PROJECT_DIR")
  if project_dir then
    return project_dir .. "/nav.json"
  end
  if quarto and quarto.project and quarto.project.directory then
    return quarto.project.directory .. "/nav.json"
  end
  return "nav.json"
end

local function load_nav()
  if nav_data then return nav_data end
  local path = get_nav_json_path()
  local f = io.open(path, "r")
  if not f then
    quarto.log.warning("exercise-nav: nav.json not found at " .. path)
    nav_data = {}
    return nav_data
  end
  local content = f:read("*a")
  f:close()
  nav_data = pandoc.json.decode(content)
  return nav_data
end

local function basename_noext(path)
  local name = path:match("([^/\\]+)$") or path
  return (name:gsub("%.%w+$", ""))
end

local function cell(class, inlines)
  return pandoc.Div({ pandoc.Plain(inlines) }, pandoc.Attr("", { class }))
end

local function get_current_input_key()
  local input_path = nil

  if quarto and quarto.doc and quarto.doc.input_file then
    if type(quarto.doc.input_file) == "function" then
      input_path = quarto.doc.input_file()
    else
      input_path = quarto.doc.input_file
    end
  end

  if not input_path then
    local files = PANDOC_STATE.input_files
    input_path = files and files[1] or nil
  end

  if not input_path then return nil end

  local name = input_path:match("([^/\\]+)$") or input_path
  return (name:gsub("%.%w+$", ""))
end

local function is_present(v)
  return v ~= nil and v ~= pandoc.json.null
end

function Pandoc(doc)
  local key = get_current_input_key()
  if not key then return doc end

  local nav = load_nav()
  local entry = nav[key]
  if not entry then return doc end

  local prev_inlines = {}
  if is_present(entry.prev) then
    prev_inlines = { pandoc.Str("← "), pandoc.Link(entry.prev.title, entry.prev.path) }
  end

  local next_inlines = {}
  if is_present(entry.next) then
    next_inlines = { pandoc.Link(entry.next.title, entry.next.path), pandoc.Str(" →") }
  end

  local back_inlines = { pandoc.Link("Back to Chapter Overview", entry.index) }

  local nav_div = pandoc.Div({
    cell("nav-prev", prev_inlines),
    cell("nav-back", back_inlines),
    cell("nav-next", next_inlines),
  }, pandoc.Attr("", { "exercise-nav" }))

  doc.blocks:insert(nav_div)
  return doc
end
