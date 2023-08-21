function populate_list(list_name, contents) {
    const list = document.getElementById(list_name)
    contents.forEach(
        content => {
            list.innerHTML += `<option value="${content}">${content}</option>`
        }
    )
}

function show_error_popup(msg) {
    document.getElementById("error-popup-wrap").classList.add("showing")
    document.getElementById("error-msg").innerHTML = msg
}

function hide_error_popup() {
    document.getElementById("error-popup-wrap").classList.remove("showing")
}

function set_input_focus(focus) {
    le_set_input_focus(focus)
}


function set_mouse_events(allow) {
    le_set_mouse_events(allow)
}


function spawn_street() {
    le_spawn_street(document.getElementById("street-module-list").value)
}


function spawn_prop() {
    le_spawn_prop(document.getElementById("prop-list").value)
}


function spawn_landmark() {
    le_spawn_landmark(
        document.getElementById("landmark-list").value,
        document.getElementById("landmark-type-list").value,
        document.getElementById("landmark-is-sz").checked,
        document.getElementById("landmark-bldg-name").value
    )
}

function select_landmark(current_title) {
    const btn = document.getElementById('rename-selected')
    if (btn.classList.contains('hidden'))
        btn.classList.remove('hidden')
    document.getElementById('landmark-bldg-name').value = current_title
}

function rename_selected_landmark() {
    le_rename_landmark(document.getElementById('landmark-bldg-name').value)
}

function deselect_landmark() {
    document.getElementById('landmark-bldg-name').value = ''
    const btn = document.getElementById('rename-selected')
    if (btn.classList.contains('hidden'))
        return
    
    btn.classList.add('hidden')
}
