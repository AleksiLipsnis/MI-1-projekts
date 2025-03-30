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

    def novērtēt_stāvoku(self, mezgls):
        if len(mezgls.skaitli) == 1:
            return mezgls.bota_punkti - mezgls.speletaja_punkti

        pāru_skaits_7 = sum(1 for i in range(len(mezgls.skaitli) - 1)
                            if mezgls.skaitli[i] + mezgls.skaitli[i + 1] == 7)

        vertējums = (pāru_skaits_7 * 2 +
                     (mezgls.bota_punkti - mezgls.speletaja_punkti) * 0.5 +
                     len(mezgls.skaitli) * 0.3)
        return vertējums

    def izveidot_spēles_koku(self, sakuma_mezgls, max_depth):
        self.visited_nodes += 1
        self.max_depth_reached = max(self.max_depth_reached, sakuma_mezgls.dziļums)

        if len(sakuma_mezgls.skaitli) == 1 or sakuma_mezgls.dziļums >= max_depth:
            sakuma_mezgls.punkti = self.novērtēt_stāvoku(sakuma_mezgls)
            return sakuma_mezgls

        for i in range(len(sakuma_mezgls.skaitli) - 1):
            rezultats = self.veikt_gajienu(sakuma_mezgls.skaitli, i, sakuma_mezgls.ir_bota_gajiens)

            if sakuma_mezgls.ir_bota_gajiens:
                jaunie_bota_punkti = sakuma_mezgls.bota_punkti + rezultats['punkti']
                jaunie_speletaja_punkti = sakuma_mezgls.speletaja_punkti
            else:
                jaunie_bota_punkti = sakuma_mezgls.bota_punkti
                jaunie_speletaja_punkti = sakuma_mezgls.speletaja_punkti + rezultats['punkti']

            bērna_mezgls = GameNode(
                rezultats['jaunie_skaitli'],
                sakuma_mezgls.dziļums + 1,
                not sakuma_mezgls.ir_bota_gajiens,
                jaunie_bota_punkti,
                jaunie_speletaja_punkti
            )
            bērna_mezgls.labakais_gajiens = i
            sakuma_mezgls.berni.append(bērna_mezgls)
            self.izveidot_spēles_koku(bērna_mezgls, max_depth)

        return sakuma_mezgls

    def minimaks(self, mezgls, dziļums, ir_bota_gajiens):
        self.visited_nodes += 1
        self.max_depth_reached = max(self.max_depth_reached, dziļums)

        if len(mezgls.skaitli) == 1 or dziļums == 0:
            mezgls.punkti = self.novērtēt_stāvoku(mezgls)
            return mezgls.punkti

        if ir_bota_gajiens:
            mezgls.punkti = -math.inf
            for bērns in mezgls.berni:
                punkti = self.minimaks(bērns, dziļums - 1, False)
                if punkti > mezgls.punkti:
                    mezgls.punkti = punkti
                    mezgls.labakais_gajiens = bērns.labakais_gajiens
        else:
            mezgls.punkti = math.inf
            for bērns in mezgls.berni:
                punkti = self.minimaks(bērns, dziļums - 1, True)
                if punkti < mezgls.punkti:
                    mezgls.punkti = punkti
                    mezgls.labakais_gajiens = bērns.labakais_gajiens

        return mezgls.punkti

    def alphabeta(self, mezgls, dziļums, alpha, beta, ir_bota_gajiens):
        self.visited_nodes += 1
        self.max_depth_reached = max(self.max_depth_reached, dziļums)

        if len(mezgls.skaitli) == 1 or dziļums == 0:
            mezgls.punkti = self.novērtēt_stāvoku(mezgls)
            return mezgls.punkti

        if ir_bota_gajiens:
            mezgls.punkti = -math.inf
            for bērns in mezgls.berni:
                punkti = self.alphabeta(bērns, dziļums - 1, alpha, beta, False)
                if punkti > mezgls.punkti:
                    mezgls.punkti = punkti
                    mezgls.labakais_gajiens = bērns.labakais_gajiens
                alpha = max(alpha, mezgls.punkti)
                if alpha >= beta:
                    break  # β nogriešana
        else:
            mezgls.punkti = math.inf
            for bērns in mezgls.berni:
                punkti = self.alphabeta(bērns, dziļums - 1, alpha, beta, True)
                if punkti < mezgls.punkti:
                    mezgls.punkti = punkti
                    mezgls.labakais_gajiens = bērns.labakais_gajiens
                beta = min(beta, mezgls.punkti)
                if beta <= alpha:
                    break  # α nogriešana

        return mezgls.punkti

    def izveleties_labako_gajienu(self, skaitli, ir_bota_gajiens):
        start_time = time.time()
        self.visited_nodes = 0
        self.max_depth_reached = 0

        sakuma_mezgls = GameNode(skaitli, 0, ir_bota_gajiens, self.bota_punkti, self.speletaja_punkti)
        self.izveidot_spēles_koku(sakuma_mezgls, self.search_depth)

        if self.use_minimax:
            self.minimaks(sakuma_mezgls, self.search_depth, ir_bota_gajiens)
        else:
            self.alphabeta(sakuma_mezgls, self.search_depth, -math.inf, math.inf, ir_bota_gajiens)

        move_time = time.time() - start_time
        self.bot_move_times.append(move_time)
        self.total_bot_moves += 1

        print(f" ")
        print(f"Apstrādāti {self.visited_nodes} mezgli")
        print(f"Gājiena laiks: {move_time:.2f} sekundes")

        return sakuma_mezgls.labakais_gajiens

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

        Label(self.objects, text="Izvēlieties meklēšanas dziļumu (1-10)",
              font=("Arial", 14), **self.label_props).pack(pady=(10, 5))

        self.depth_scale = Scale(self.objects, from_=1, to=10, orient=HORIZONTAL,
                                 bg="lightblue", activebackground="blue", length=200)
        self.depth_scale.set(3)  # Default depth
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

        self.numbers_list = [random.randrange(1, 10) for _ in range(self.selected_range)]
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
        self.game_active = True
        self.selected_indices = []
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
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        for widget in self.current_frame.winfo_children():
            widget.destroy()

        # Rādām vēsturi
        for entry in self.history:
            frame = Frame(self.history_frame, bg="lightblue")
            frame.pack(anchor="w", pady=(0, 5))

            Label(frame, text=f"Gājiens {entry['gajiena_nr']}: {entry['info']}",
                  font=("Arial", 10), **self.label_props).pack(side="left")

            for i, num in enumerate(entry['skaitli']):
                bg_color = "yellow" if entry['izvele'] and i in entry['izvele'] else "white"
                Label(frame, text=str(num), font=("Arial", 12), width=3,
                      relief="ridge", bg=bg_color).pack(side="left")

            Label(frame,
                  text=f"Punkti: Spēlētājs={entry['speletaja_punkti']}, Bots={entry['bota_punkti']}",
                  font=("Arial", 10), **self.label_props).pack(side="left", padx=10)

        # Rādām pašreizējo stāvokli
        current_frame = Frame(self.current_frame, bg="lightblue")
        current_frame.pack(pady=(10, 0))

        Label(current_frame, text="Pašreizējais stāvoklis:",
              font=("Arial", 12), **self.label_props).pack(side="left")

        self.buttons = []
        for i, num in enumerate(self.numbers_list):
            btn = Button(current_frame, text=str(num), font=("Arial", 14), width=4, height=2,
                         command=lambda i=i: self.select_number(i))
            btn.pack(side="left", padx=2)
            self.buttons.append(btn)

        self.score_label.config(text=f"Spēlētājs: {self.speletaja_punkti} | Bots: {self.bota_punkti}")

    def select_number(self, index):
        if not self.game_active:
            return

        # Ja jau ir izvēlēti 2 skaitļi, sākam jaunu izvēli
        if len(self.selected_indices) == 2:
            self.selected_indices = []
            self.update_button_colors()

        # Pievienojam jauno izvēli
        if index not in self.selected_indices:
            self.selected_indices.append(index)
            self.buttons[index].configure(bg="yellow")

        # Ja ir izvēlēti 2 skaitļi, pārbaudam vai tie ir kaimiņi
        if len(self.selected_indices) == 2:
            # Sakārtojam indeksus augošā secībā
            self.selected_indices.sort()

            # Pārbaudam vai skaitļi ir kaimiņi
            if abs(self.selected_indices[0] - self.selected_indices[1]) == 1:
                self.make_move(self.selected_indices, False)
            else:
                # Ja nav kaimiņi, sākam jaunu izvēli
                messagebox.showwarning("Kļūda", "Jāizvēlas kaimiņu skaitļi!")
                self.selected_indices = []
                self.update_button_colors()
                return

            self.selected_indices = []
            if len(self.numbers_list) > 1:
                self.master.after(1000, self.bot_move)

    def make_move(self, indices, is_bot_move):
        if len(indices) != 2 or abs(indices[0] - indices[1]) != 1:
            return

        rezultats = self.veikt_gajienu(self.numbers_list, indices[0], is_bot_move)

        # Atjauninam punktus
        if is_bot_move:
            self.bota_punkti += rezultats['punkti']
        else:
            self.speletaja_punkti += rezultats['punkti']

        # Pievienojam vēsturei
        self.history.append({
            'skaitli': rezultats['vecie_skaitli'],
            'info': f"{'Bots' if is_bot_move else 'Spēlētājs'}: {rezultats['gajiena_info']}",
            'bota_punkti': self.bota_punkti,
            'speletaja_punkti': self.speletaja_punkti,
            'gajiena_nr': len(self.history),
            'izvele': rezultats['izvele']
        })

        # Atjauninam pašreizējo stāvokli
        self.numbers_list = rezultats['jaunie_skaitli']

        self.update_game_ui()
        self.check_game_end()

    def bot_move(self):
        if not self.game_active or len(self.numbers_list) <= 1:
            return

        move_index = self.izveleties_labako_gajienu(self.numbers_list, True)
        if move_index is not None and move_index < len(self.numbers_list) - 1:
            self.make_move([move_index, move_index + 1], True)

    def check_game_end(self):
        if len(self.numbers_list) <= 1:
            self.game_active = False

            # Calculate average move time
            avg_time = sum(self.bot_move_times) / len(self.bot_move_times) if self.bot_move_times else 0

            winner = "Neizšķirts!"
            if self.speletaja_punkti > self.bota_punkti:
                winner = "Spēlētājs uzvarēja!"
            elif self.bota_punkti > self.speletaja_punkti:
                winner = "Bots uzvarēja!"

            stats_message = (
                f"{winner}\n\n"
                f"Spēlētājs: {self.speletaja_punkti}\n"
                f"Bots: {self.bota_punkti}\n\n"
                f"Statistika:\n"
                f"Vidējais gājiena laiks: {avg_time:.4f} sekundes"
            )

            messagebox.showinfo("Spēle beigusies!", stats_message)

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
