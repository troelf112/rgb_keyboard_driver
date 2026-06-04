import FreeSimpleGUI as sg
from PySide6.QtWidgets import QApplication, QColorDialog
from pathlib import Path
from systemd_handling import update_service

qt_app = QApplication([])

command = 'sudo sh -c "echo \'255 255 255\' > /sys/devices/platform/tuxedo_keyboard/leds/rgb:kbd_backlight/multi_intensity"'

def choose_color() -> list[int]:
    color = QColorDialog.getColor()

    if color.isValid():
        rgb = [color.red(), color.green(), color.blue()]
        return list(map(int, rgb))
    else:
        return [0,0,0]

def toggle_visability(elements:list, enable:bool) -> None:
    for element in elements:
        element.update(visible=enable)

layout = [
    [sg.Check(key="chb_static", text="Static backlight", enable_events=True, default=True)],
    [sg.Input(key='input_colour'), sg.Button('Select color', enable_events=True, key='btn_select')],
    [sg.Check(key="chb_rainbow", text="Rainbow Effect", enable_events=True)],
    [
        sg.Text('increasing steps: ', visible=False),
        sg.Input(key='input_interval', default_text="1", visible=False),
        sg.Text('delay: ', visible=False),
        sg.Input(key='input_delay', default_text="0.05", visible=False),
        sg.Text('Filepath: ', visible=False),
        sg.Input(key='input_file', default_text="/sys/devices/platform/tuxedo_keyboard/leds/rgb:kbd_backlight/multi_intensity", visible=False),
        sg.FileBrowse(target='input_file', visible=False),
        sg.Check("verbose", visible=False, key='verbose')
    ],
    [sg.Button("OK")]
]

window = sg.Window("Keyboard RGB Controller", layout)
color = [255, 255, 255]

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED:
        break

    if event == "OK":
        if window['chb_rainbow'].get():
            assert not window['chb_static'].get()

            script_path = Path(__file__).resolve()
            script_dir = script_path.parent

            try:
                interval = int(values['input_interval'])
            except ValueError:
                interval = 1

            try:
                delay = float(values['input_delay'])
            except ValueError:
                delay = 0.05

            command = f"/usr/bin/python3 {script_dir}/effects.py --interval {interval} --delay {delay}"

            file = Path(values['input_file'])
            if file.is_file():
                command += f" --file {values['input_file']}"

            if window['verbose'].get():
                command += " --verbose"

        elif window['chb_static'].get():
            command = f'/bin/sh -c \'echo "{' '.join(map(str, color))}" > /sys/devices/platform/tuxedo_keyboard/leds/rgb:kbd_backlight/multi_intensity\''
        else:
            command = '/bin/sh -c \'echo "0 0 0" > /sys/devices/platform/tuxedo_keyboard/leds/rgb:kbd_backlight/multi_intensity\''

        print(command)
        update_service(command)
        break

    if event == "btn_select":
        color = choose_color()
        window['input_colour'].update(value=', '.join(map(str, color)))

    if event == "chb_rainbow":
        if values['chb_rainbow']:
            window['chb_static'].update(value=False)
        toggle_visability(layout[1], window['chb_static'].get())
        toggle_visability(layout[3], window['chb_rainbow'].get())

    if event == "chb_static":
        if values['chb_static']:
            window['chb_rainbow'].update(value=False)
        toggle_visability(layout[1], window['chb_static'].get())
        toggle_visability(layout[3], window['chb_rainbow'].get())

window.close()
