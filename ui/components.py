
import customtkinter as ctk

class MultiRowTabview(ctk.CTkFrame):
    """
    A custom TabView that arranges tab buttons in multiple rows.
    Supports detaching tabs into separate windows via Right-Click.
    """
    def __init__(self, master, 
                 fg_color=None, 
                 btn_fg_color=None,
                 btn_hover_color=None,
                 btn_selected_color=None,
                 btn_text_color=None,
                 btn_selected_text_color=None,
                 command_right_click=None,
                 **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.main_fg_color = fg_color
        self.btn_fg_color = btn_fg_color
        self.btn_hover_color = btn_hover_color
        self.btn_selected_color = btn_selected_color
        self.btn_text_color = btn_text_color
        self.btn_selected_text_color = btn_selected_text_color
        self.command_right_click = command_right_click
        
        # Frame for buttons (Top)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="top", fill="x", pady=(0, 5))
        
        # Rows for buttons
        self.row1 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        self.row1.pack(side="top", fill="x", pady=(0, 2))
        self.row2 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        self.row2.pack(side="top", fill="x")
        
        # Content frame (Bottom)
        self.content_frame = ctk.CTkFrame(self, fg_color=self.main_fg_color, corner_radius=10)
        self.content_frame.pack(side="bottom", fill="both", expand=True)
        
        self.tabs = {}     # name -> frame
        self.buttons = {}  # name -> button
        self.popped_windows = set() # Set of names of popped out tabs
        self.current_tab = None

    def add(self, name):
        # Create the tab content frame
        frame = ctk.CTkFrame(self.content_frame, fg_color=self.main_fg_color, corner_radius=0)
        self.tabs[name] = frame
        
        # Decide which row to put the button in (Split 6 / rest)
        if len(self.buttons) < 6:
            parent = self.row1
        else:
            parent = self.row2
            
        # Create the button
        btn = ctk.CTkButton(parent, text=name,
                            fg_color=self.btn_fg_color,
                            hover_color=self.btn_hover_color,
                            text_color=self.btn_text_color,
                            corner_radius=6,
                            height=28,
                            width=80, # Allow expanding
                            command=lambda: self.set(name))
        
        btn.pack(side="left", fill="x", expand=True, padx=2)
        
        # Bind Right Click if callback provided
        if self.command_right_click:
            btn.bind("<Button-3>", lambda event, n=name: self.command_right_click(n))
        
        self.buttons[name] = btn
        return frame

    def set(self, name):
        if name not in self.tabs:
            return
        
        # Hide all tabs
        for f in self.tabs.values():
            f.pack_forget()
            
        # Reset all buttons color
        for n, b in self.buttons.items():
            is_popped = n in self.popped_windows
            if n == name:
                b.configure(fg_color=self.btn_selected_color)
                if self.btn_selected_text_color:
                    b.configure(text_color=self.btn_selected_text_color)
            else:
                b.configure(fg_color=self.btn_fg_color if not is_popped else "gray20")
                b.configure(text_color=self.btn_text_color if not is_popped else "gray60")
                
        # Show selected tab (only if not popped out)
        if name not in self.popped_windows:
            self.tabs[name].pack(fill="both", expand=True, padx=5, pady=5)
            
        self.current_tab = name
        
    def pop_out(self, name):
        """Marque l'onglet comme détaché (visuel uniquement)."""
        self.popped_windows.add(name)
        self.buttons[name].configure(text=f"❐ {name}")
        # Masquer le contenu si c'était l'onglet actif
        if self.current_tab == name:
            self.tabs[name].pack_forget()
        self.set(self.current_tab) # Rafraîchir les couleurs

    def dock_in(self, name):
        """Marque l'onglet comme rattaché (visuel uniquement)."""
        if name in self.popped_windows:
            self.popped_windows.remove(name)
            self.buttons[name].configure(text=name)
            # Réafficher si c'est l'onglet actif
            if self.current_tab == name:
                self.tabs[name].pack(fill="both", expand=True, padx=5, pady=5)
            self.set(self.current_tab) # Rafraîchir les couleurs
        
    def get(self):
        return self.current_tab
