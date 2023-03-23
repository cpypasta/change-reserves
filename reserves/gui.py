import PySimpleGUI as sg
from reserves import logo, update

def main() -> None:
    sg.theme("DarkAmber")

    layout = [[
      sg.Image(logo.value), 
      sg.Column([
        [sg.T("Reserve Changer", font="_ 24")],
        [sg.Checkbox("Update From Modded?", k="modded")],
        [sg.Checkbox("Update Population?", k="update_pop"), sg.T("   X"), sg.Input(s=4, default_text="2", k="pop_multiplier")],
        [sg.Checkbox("Update Deployables?", k="update_deploy"), sg.T("X"), sg.Input(s=4, default_text="2", k="deploy_multiplier")],
        [sg.Button("UPDATE", expand_x=True)]
      ])
    ]]

    window = sg.Window("Reserve Changer", layout, font="_ 16", icon=logo.value)

    while True:
      event, values = window.read()
      print(event, values)
      if event == sg.WIN_CLOSED:
         break
      if event == "UPDATE":
        update_pop = values["update_pop"]
        update_deploy = values["update_deploy"]
        modded = values["modded"]
        pop_multiply = int(values["pop_multiplier"])
        deploy_multiply = int(values["deploy_multiplier"])
        source_path = update.get_mod_path() if modded else update.SOURCE_PATH
        try:
          mod_path = update.process(source_path, update_pop, update_deploy, pop_multiply, deploy_multiply)
          sg.Popup(f"Successfully saved the updates to:\n\n {mod_path}\n", title="Success", icon=logo.value, font="_ 15")
        except Exception as ex:
          sg.Popup(f"ERROR: {ex}", title="Error", icon=logo.value, font="_ 15") 
    
    window.close()

if __name__ == "__main__":
    main()