import tkinter as tk
from tkinter import Frame, Label, Button, Scale, HORIZONTAL, messagebox
import random
import time
import math


class GameNode:
    """Klase spēles koka mezglu glabāšanai"""

    def __init__(self, skaitli, dziļums=0, ir_bota_gajiens=True, bota_punkti=0, speletaja_punkti=0):
        self.skaitli = skaitli
        self.dziļums = dziļums
        self.ir_bota_gajiens = ir_bota_gajiens
        self.berni = []
        self.punkti = None
        self.labakais_gajiens = None
        self.bota_punkti = bota_punkti
        self.speletaja_punkti = speletaja_punkti


class NumberGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Spēle ar skaitļu virkni")
        self.master.minsize(300, 600)
        self.master.configure(bg="lightblue", padx=10, pady=10)

        self.label_props = {'background': 'lightblue'}
        self.button_props = {'width': 20, 'font': ("Arial", 12)}

        self.numbers_list = []
        self.history = []
        self.selected_range = 0
        self.selected_indices = []
        self.bota_punkti = 0
        self.speletaja_punkti = 0
        self.bots_sāk = False
        self.game_active = False
        self.buttons = []
        self.use_minimax = True
        self.search_depth = 3  # Default depth

        # Statistika
        self.visited_nodes = 0
        self.bot_move_times = []
        self.total_bot_moves = 0
        self.max_depth_reached = 0

        self.create_main_screen()

    def veikt_gajienu(self, skaitli, indekss, ir_bota_gajiens):
        a, b = skaitli[indekss], skaitli[indekss + 1]
        para_summa = a + b

        if para_summa > 7:
            jauna_vertiba = 1
            punkti = 1
        elif para_summa < 7:
            jauna_vertiba = 3
            punkti = -1
        else:
            jauna_vertiba = 2
            punkti = 2

        jaunie_skaitli = skaitli[:indekss] + [jauna_vertiba] + skaitli[indekss + 2:]

        return {
            'vecie_skaitli': skaitli.copy(),
            'jaunie_skaitli': jaunie_skaitli,
            'punkti': punkti,
            'gajiena_info': f"{a}+{b}={para_summa} -> {jauna_vertiba}",
            'ir_bota_gajiens': ir_bota_gajiens,
            'izvele': [indekss, indekss + 1]
        }
    
    def novertet_stavokli(self, mezgls):
        if len(mezgls.skaitli) == 1:
            return mezgls.bota_punkti - mezgls.speletaja_punkti

        pāru_skaits_7 = sum(1 for i in range(len(mezgls.skaitli) - 1)
                            if mezgls.skaitli[i] + mezgls.skaitli[i + 1] == 7)

        vertējums = (pāru_skaits_7 * 2 +
                     (mezgls.bota_punkti - mezgls.speletaja_punkti) * 0.5 +
                     len(mezgls.skaitli) * 0.3)
        return vertējums
    
    def izveidot_speles_koku(self, mezgls, dziļums):
        if dziļums == 0 or len(mezgls.skaitli) < 2:
            return

        self.visited_nodes += 1
        self.max_depth_reached = max(self.max_depth_reached, mezgls.dziļums)

        for i in range(len(mezgls.skaitli) - 1):
            rezultats = self.veikt_gajienu(mezgls.skaitli, i, mezgls.ir_bota_gajiens)

            jaunais_mezgls = GameNode(
                rezultats['jaunie_skaitli'],
                dziļums=mezgls.dziļums + 1,
                ir_bota_gajiens=not mezgls.ir_bota_gajiens,
                bota_punkti=mezgls.bota_punkti + rezultats['punkti'] if mezgls.ir_bota_gajiens else mezgls.bota_punkti,
                speletaja_punkti=mezgls.speletaja_punkti + rezultats['punkti'] if not mezgls.ir_bota_gajiens else mezgls.speletaja_punkti
            )

            self.izveidot_speles_koku(jaunais_mezgls, dziļums - 1)
            mezgls.berni.append((jaunais_mezgls, rezultats))

    def minimax(self, mezgls, dziļums, ir_bota_gajiens):
        if dziļums == 0 or len(mezgls.skaitli) < 2:
            return self.novertet_stavokli(mezgls)

        if ir_bota_gajiens:
            labaka_vertiba = -math.inf
            for i in range(len(mezgls.skaitli) - 1):
                rezultats = self.veikt_gajienu(mezgls.skaitli, i, True)
                bernu_mezgls = GameNode(
                    rezultats['jaunie_skaitli'],
                    dziļums=mezgls.dziļums + 1,
                    ir_bota_gajiens=False,
                    bota_punkti=mezgls.bota_punkti + rezultats['punkti'],
                    speletaja_punkti=mezgls.speletaja_punkti
                )
                vertiba = self.minimax(bernu_mezgls, dziļums - 1, False)
                if vertiba > labaka_vertiba:
                    labaka_vertiba = vertiba
                    mezgls.labakais_gajiens = rezultats
            return labaka_vertiba
        else:
            sliktaka_vertiba = math.inf
            for i in range(len(mezgls.skaitli) - 1):
                rezultats = self.veikt_gajienu(mezgls.skaitli, i, False)
                bernu_mezgls = GameNode(
                    rezultats['jaunie_skaitli'],
                    dziļums=mezgls.dziļums + 1,
                    ir_bota_gajiens=True,
                    bota_punkti=mezgls.bota_punkti,
                    speletaja_punkti=mezgls.speletaja_punkti + rezultats['punkti']
                )
                vertiba = self.minimax(bernu_mezgls, dziļums - 1, True)
                if vertiba < sliktaka_vertiba:
                    sliktaka_vertiba = vertiba
                    mezgls.labakais_gajiens = rezultats
            return sliktaka_vertiba

    def alphabeta(self, mezgls, dziļums, alfa, beta, ir_bota_gajiens):
        if dziļums == 0 or len(mezgls.skaitli) < 2:
            return self.novertet_stavokli(mezgls)

        if ir_bota_gajiens:
            labaka_vertiba = -math.inf
            for i in range(len(mezgls.skaitli) - 1):
                rezultats = self.veikt_gajienu(mezgls.skaitli, i, True)
                bernu_mezgls = GameNode(
                    rezultats['jaunie_skaitli'],
                    dziļums=mezgls.dziļums + 1,
                    ir_bota_gajiens=False,
                    bota_punkti=mezgls.bota_punkti + rezultats['punkti'],
                    speletaja_punkti=mezgls.speletaja_punkti
                )
                self.visited_nodes += 1
                vertiba = self.alphabeta(bernu_mezgls, dziļums - 1, alfa, beta, False)
                if vertiba > labaka_vertiba:
                    labaka_vertiba = vertiba
                    mezgls.labakais_gajiens = rezultats
                alfa = max(alfa, labaka_vertiba)
                if beta <= alfa:
                    break  # β nogriešana
            return labaka_vertiba
        else:
            sliktaka_vertiba = math.inf
            for i in range(len(mezgls.skaitli) - 1):
                rezultats = self.veikt_gajienu(mezgls.skaitli, i, False)
                bernu_mezgls = GameNode(
                    rezultats['jaunie_skaitli'],
                    dziļums=mezgls.dziļums + 1,
                    ir_bota_gajiens=True,
                    bota_punkti=mezgls.bota_punkti,
                    speletaja_punkti=mezgls.speletaja_punkti + rezultats['punkti']
                )
                self.visited_nodes += 1
                vertiba = self.alphabeta(bernu_mezgls, dziļums - 1, alfa, beta, True)
                if vertiba < sliktaka_vertiba:
                    sliktaka_vertiba = vertiba
                    mezgls.labakais_gajiens = rezultats
                beta = min(beta, sliktaka_vertiba)
                if beta <= alfa:
                    break  # α nogriešana
            return sliktaka_vertiba
        
    def izveleties_labako_gajienu(self, skaitli, ir_bota_gajiens):
        sakuma_laiks = time.time()

        # Statistika pirms izsaukuma
        self.visited_nodes = 0
        self.max_depth_reached = 0

        saknes_mezgls = GameNode(skaitli, 0, ir_bota_gajiens, self.bota_punkti, self.speletaja_punkti)
        self.izveidot_speles_koku(saknes_mezgls, self.search_depth)

        if self.use_minimax:
            self.minimax(saknes_mezgls, self.search_depth, ir_bota_gajiens)
        else:
            self.alphabeta(saknes_mezgls, self.search_depth, -math.inf, math.inf, ir_bota_gajiens)

        gajiena_laiks = time.time() - sakuma_laiks
        self.bot_move_times.append(gajiena_laiks)
        self.total_bot_moves += 1

        print(f" ")
        print(f"Apstrādāti {self.visited_nodes} mezgli")
        print(f"Gājiena laiks: {gajiena_laiks:.2f} sekundes")

        return saknes_mezgls.labakais_gajiens
    
    def create_main_screen(self):
        self.clear_screen()

        self.objects = Frame(self.master, bg="lightblue")
        self.objects.pack(expand=True)

        Label(self.objects, text="Spēle ar skaitļu virkni", font=("Arial", 18), **self.label_props).pack()
        Label(self.objects, text="Lai sāktu spēli izvēlieties virknes garumu",
              font=("Arial", 14), **self.label_props).pack()

        self.numbers_range = Scale(self.objects, from_=15, to=25, orient=HORIZONTAL,
                                   bg="lightblue", activebackground="blue", length=200)
        self.numbers_range.pack(pady=(10, 5))

        Label(self.objects, text="Izvēlieties meklēšanas dziļumu (1-9)",
              font=("Arial", 14), **self.label_props).pack(pady=(10, 5))

        self.depth_scale = Scale(self.objects, from_=1, to=9, orient=HORIZONTAL,
                                 bg="lightblue", activebackground="blue", length=200)
        self.depth_scale.set(3)  # Noklusejuma dzilums
        self.depth_scale.pack(pady=(10, 5))

        Button(self.objects, text="Turpināt", **self.button_props,
               bg="lightgreen", command=self.choose_starter).pack(pady=(20, 10))

    def choose_starter(self):
        self.selected_range = self.numbers_range.get()
        self.search_depth = self.depth_scale.get()  # Set the selected depth
        self.clear_screen()

        self.objects = Frame(self.master, bg="lightblue")
        self.objects.pack(expand=True)

        Label(self.objects, text="Izvēlieties, kurš sāks spēli",
              font=("Arial", 14), **self.label_props).pack(pady=(10, 5))

        Button(self.objects, text="Cilvēks", **self.button_props,
               bg="lightblue", command=lambda: self.set_starter(False)).pack(pady=5)

        Button(self.objects, text="Mašīna", **self.button_props,
               bg="lightblue", command=lambda: self.set_starter(True)).pack(pady=5)
        
    def set_starter(self, bots_sāk):
        self.bots_sāk = bots_sāk
        self.choose_algorithm()

    def choose_algorithm(self):
        self.clear_screen()

        self.objects = Frame(self.master, bg="lightblue")
        self.objects.pack(expand=True)

        Label(self.objects, text="Izvēlieties algoritmu",
              font=("Arial", 14), **self.label_props).pack(pady=(10, 5))

        Button(self.objects, text="Minimaksa algoritmu", **self.button_props,
               bg="lightblue", command=self.start_minimax_game).pack(pady=5)

        Button(self.objects, text="Alfa-beta algoritmu", **self.button_props,
               bg="lightblue", command=self.start_alphabeta_game).pack(pady=5)

    def start_minimax_game(self):
        self.use_minimax = True
        self.start_game()

    def start_alphabeta_game(self):
        self.use_minimax = False
        self.start_game()

    def start_game(self):
         # Reset statistics for new game
        self.visited_nodes = 0
        self.bot_move_times = []
        self.total_bot_moves = 0

        self.numbers_list = [random.randint(1, 9) for _ in range(self.selected_range)]
        self.history = [{
            'skaitli': self.numbers_list.copy(),
            'info': "Sākuma stāvoklis",
            'bota_punkti': 0,
            'speletaja_punkti': 0,
            'gajiena_nr': 0,
            'izvele': None
        }]
        self.bota_punkti = 0
        self.speletaja_punkti = 0
        self.selected_indices = []
        self.game_active = True

        self.clear_screen()

        self.game_frame = Frame(self.master, bg="lightblue")
        self.game_frame.pack(expand=True, fill="both")

        self.score_label = Label(self.game_frame,
                                 text=f"Spēlētājs: {self.speletaja_punkti} | Bots: {self.bota_punkti}",
                                 font=("Arial", 14), bg="lightblue")
        self.score_label.pack(pady=(0, 10))

        self.history_frame = Frame(self.game_frame, bg="lightblue")
        self.history_frame.pack(fill="x", pady=(0, 10))

        self.current_frame = Frame(self.game_frame, bg="lightblue")
        self.current_frame.pack()

        self.update_game_ui()

        if self.bots_sāk:
            self.bot_move()

    def update_game_ui(self):
        # Notīra vēstures un pašreizējās virknes logus
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        for widget in self.current_frame.winfo_children():
            widget.destroy()

         # Gājienu vēstures attēlošana
        for entry in self.history:
            frame = Frame(self.history_frame, bg="lightblue")
            frame.pack(anchor="w", pady=(2, 2), fill="x", padx=5)

            Label(frame, text=f"Gājiens {entry['gajiena_nr']}: {entry['info']}",
                  font=("Arial", 10), **self.label_props).pack(side="left")
            
            for i, num in enumerate(entry['skaitli']):
                bg_color = "yellow" if entry['izvele'] and i in entry['izvele'] else "white"
                Label(frame, text=str(num), font=("Arial", 12), width=3,
                      relief="ridge", bg=bg_color).pack(side="left")

            Label(frame,
                  text=f"Punkti: Spēlētājs={entry['speletaja_punkti']}, Bots={entry['bota_punkti']}",
                  font=("Arial", 10), **self.label_props).pack(side="left", padx=10)

        # Pašreizējais stāvoklis
        current_frame = Frame(self.current_frame, bg="lightblue")
        current_frame.pack(pady=(10, 0))

        Label(current_frame, text="Pašreizējais stāvoklis:",
            font=("Arial", 12), **self.label_props).pack(side="left")
        
        self.buttons = []
        for i, num in enumerate(self.numbers_list):
            btn = Button(current_frame, text=str(num), width=4, font=("Arial", 14),
                        command=lambda i=i: self.select_number(i))
            btn.pack(side="left", padx=2)
            self.buttons.append(btn)

        # Atjauno punktus
        self.score_label.config(text=f"Spēlētājs: {self.speletaja_punkti} | Bots: {self.bota_punkti}")

    def select_number(self, index):
        if not self.game_active:
            return
        
        # Ja jau ir izvēlēti 2 skaitļi, sākam jaunu izvēli
        if len(self.selected_indices) == 2:
            self.selected_indices = []
            self.update_button_colors()
        
         # Ja tas ir pirmais klikšķis
        if index not in self.selected_indices:
            self.selected_indices.append(index)
            self.buttons[index].config(bg="yellow")

        # Ja jau ir izvēlēti 2 skaitļi, sākam jaunu izvēli
        if len(self.selected_indices) == 2:
            self.selected_indices.sort()

            # Jābūt blakus skaitļiem
            if abs(self.selected_indices[0] - self.selected_indices[1]) == 1:
                 self.make_move(self.selected_indices, False)
                 
                 if self.game_active:
                    self.master.after(500, self.bot_move)
            else:
                # Nav blakus – atiestata izvēli
                messagebox.showwarning("Kļūda", "Jāizvēlas kaimiņu skaitļi!")
                self.selected_indices = []
                self.update_button_colors()
                return
            
            self.selected_indices = []

    def make_move(self, indices, is_bot_move):
        if len(indices) != 2 or abs(indices[0] - indices[1]) != 1:
            return

        rezultats = self.veikt_gajienu(self.numbers_list, indices[0], is_bot_move)

        # Atjaunot punktus
        if is_bot_move:
            self.bota_punkti += rezultats['punkti']
        else:
            self.speletaja_punkti += rezultats['punkti']

        # Gājienu piefiksēšana vēsturē
        self.history.append({
            'skaitli': rezultats['vecie_skaitli'],
            'info': f"{'Bots' if is_bot_move else 'Spēlētājs'}: {rezultats['gajiena_info']}",
            'bota_punkti': self.bota_punkti,
            'speletaja_punkti': self.speletaja_punkti,
            'gajiena_nr': len(self.history),
            'izvele': rezultats['izvele']
        })

        self.numbers_list = rezultats['jaunie_skaitli']

        self.update_game_ui()
        if len(self.numbers_list) <= 1:
            self.beigt_speli()

    def bot_move(self):
        if not self.game_active or len(self.numbers_list) <= 1:
            return
        
        gajiens = self.izveleties_labako_gajienu(self.numbers_list, True)

        if gajiens and 'izvele' in gajiens:
            self.make_move(gajiens['izvele'], True)
        

    def beigt_speli(self):
        if len(self.numbers_list) <= 1:
            self.game_active = False

        # Aprēķināt vidējo bota gājiena laiku
        if self.bot_move_times:
            videjais_laiks = sum(self.bot_move_times) / len(self.bot_move_times)
            videjais_laiks = round(videjais_laiks, 3)
        else:
            videjais_laiks = 0.0   

        # Noteikt uzvarētāju
        if self.bota_punkti > self.speletaja_punkti:
            rezultats = "Uzvarēja BOTS!"
        elif self.speletaja_punkti > self.bota_punkti:
            rezultats = "Uzvarēja SPĒLĒTĀJS!"
        else:
            rezultats = "Neizšķirts!"

        # Izveidot ziņojumu
        statistika = f"""
            Rezultāts: {rezultats}

            Spēlētāja punkti: {self.speletaja_punkti}
            Bota punkti: {self.bota_punkti}

            Vidējais gājiena laiks: {videjais_laiks} sekundes
            """

        messagebox.showinfo("Spēles beigas", statistika)

        Button(self.game_frame, text="Jauna spēle", **self.button_props,
                   bg="lightgreen", command=self.create_main_screen).pack(pady=20)
    
    def update_button_colors(self):
        for btn in self.buttons:
            btn.configure(bg="SystemButtonFace")

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = NumberGame(root)
    root.mainloop()
