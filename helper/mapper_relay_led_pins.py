# file: map_hardware_hybrid.py

import time
import sys
import threading
from gpiozero import Button, LED

# 1. Defina os pinos BCM que você conectou.
ALL_BUTTON_PINS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13]
ALL_RELAY_PINS  = [14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]

# --- Variáveis de Estado Global ---
# Usadas para comunicação entre a thread principal e a thread do relé.
active_relay_pin = None
relay_thread_stop_event = threading.Event()

# --- Funções do Hardware ---

def initialize_gpio():
    """Inicializa todos os componentes GPIO com configurações robustas."""
    print("Inicializando componentes GPIO...")
    try:
        # A inicialização é a chave para a robustez:
        # 1. `pull_up=True`: Evita o estado "flutuante", garantindo um sinal estável.
        # 2. `bounce_time=0.1`: Filtra o ruído elétrico (debounce) do botão físico.
        buttons = {pin: Button(pin, pull_up=True, bounce_time=0.1) for pin in ALL_BUTTON_PINS}
        relays = {pin: LED(pin, active_high=False) for pin in ALL_RELAY_PINS}
        print("GPIO inicializado com sucesso.")
        return buttons, relays
    except Exception as e:
        print(f"\n!!! ERRO DE INICIALIZAÇÃO GPIO: {e} !!!")
        print("Verifique se a biblioteca lgpio está instalada (`pip install lgpio`).")
        print("Verifique se os números dos pinos estão corretos e não estão em conflito.")
        return None, None

def cleanup(buttons, relays):
    """Garante a liberação segura de todos os recursos GPIO."""
    print("\nLimpando recursos GPIO...")
    relay_thread_stop_event.set()
    all_components = list(buttons.values()) + list(relays.values())
    for component in all_components:
        component.close()
    print("Concluído.")

def wait_for_any_press(buttons, already_mapped_pins):
    """
    Função de polling bloqueante e robusta.
    Espera até que um botão não mapeado seja pressionado e o retorna.
    """
    while True:
        for pin, button in buttons.items():
            if button.is_pressed:
                # Aguarda o usuário soltar para evitar leituras múltiplas
                while button.is_pressed:
                    time.sleep(0.05)
                
                if pin in already_mapped_pins:
                    print(f"\nAVISO: O botão no pino {pin} já foi mapeado. Pressione outro.")
                    # Continua o loop externo para esperar por um botão diferente
                    continue
                
                return pin # Retorna o pino do botão recém-pressionado
        time.sleep(0.01) # Pequena pausa para não sobrecarregar o CPU

def relay_cycler_task(relays, unmapped_relays):
    """
    Thread que cicla os LEDs não mapeados. Comunica o LED ativo
    através da variável global `active_relay_pin`.
    """
    global active_relay_pin
    while not relay_thread_stop_event.is_set():
        for pin in unmapped_relays:
            if relay_thread_stop_event.is_set(): break
            active_relay_pin = pin
            relays[active_relay_pin].on()
            sys.stdout.write(f"\r  -> Testando Relé no pino {active_relay_pin}... ")
            sys.stdout.flush()
            time.sleep(0.75) # Tempo de ciclo ajustado
            if relay_thread_stop_event.is_set(): break
            relays[active_relay_pin].off()

# --- Fluxo Principal do Script ---
if __name__ == "__main__":
    buttons, relays = initialize_gpio()
    if not buttons:
        exit()

    ordered_buttons = []
    ordered_relays = []

    try:
        num_slots = len(ALL_BUTTON_PINS)
        while len(ordered_buttons) < num_slots:
            current_slot = len(ordered_buttons) + 1
            
            # --- FASE 1: Identificar o Botão ---
            print(f"\n--- SLOT #{current_slot}/{num_slots} | FASE 1: IDENTIFICAR BOTÃO ---")
            print("Pressione o próximo botão físico que deseja mapear.")
            
            found_button_pin = wait_for_any_press(buttons, ordered_buttons)
            print(f"Botão no pino {found_button_pin} identificado.")
            
            # --- FASE 2: Identificar o Relé ---
            print(f"\n--- SLOT #{current_slot}/{num_slots} | FASE 2: IDENTIFICAR RELÉ ---")
            
            unmapped_relays = [pin for pin in ALL_RELAY_PINS if pin not in ordered_relays]
            relay_thread_stop_event.clear()
            
            cycler_thread = threading.Thread(target=relay_cycler_task, args=(relays, unmapped_relays))
            cycler_thread.start()
            
            print("Quando o LED desejado acender, PRESSIONE O MESMO BOTÃO FÍSICO NOVAMENTE.")
            
            # Usa o mesmo mecanismo de polling robusto para esperar o segundo pressionamento
            target_button = buttons[found_button_pin]
            while not target_button.is_pressed:
                time.sleep(0.01)
            
            # Botão pressionado, pare a thread de ciclagem
            relay_thread_stop_event.set()
            cycler_thread.join()
            
            confirmed_relay_pin = active_relay_pin
            
            # Registra o mapeamento
            ordered_buttons.append(found_button_pin)
            ordered_relays.append(confirmed_relay_pin)
            
            print(f"\n\nMAPEAMENTO CONFIRMADO PARA O SLOT #{current_slot}:")
            print(f"  - Botão (Pino {found_button_pin}) <=> Relé (Pino {confirmed_relay_pin})")
            print("----------------------------------------------------")
            
            # Aguarda o usuário soltar o botão para não iniciar a próxima fase imediatamente
            while target_button.is_pressed:
                time.sleep(0.05)

        # --- Finalização ---
        print("\n\n====================================================")
        print("MAPEAMENTO COMPLETO!")
        print("Copie estas listas para o seu arquivo 'config.py':")
        print(f"\nBUTTON_PINS = {ordered_buttons}")
        print(f"RELAY_PINS  = {ordered_relays}")
        print("\n====================================================")

    except (KeyboardInterrupt, Exception) as e:
        if isinstance(e, Exception): print(f"ERRO: {e}")
        print("\nOperação cancelada.")
    finally:
        cleanup(buttons, relays)