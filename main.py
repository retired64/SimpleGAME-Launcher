import gi
import sys
import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict, Optional

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango
gi.repository.GLib.set_prgname('pixellauncher')
# ============================================================================
# CONFIGURACIÓN Y CONSTANTES ;)
# ============================================================================
APP_NAME = "Pixel Launcher Pro"
APP_VERSION = "3.0"
CONFIG_DIR = Path.home() / ".local" / "share" / "pixel-launcher"
GAMES_JSON = CONFIG_DIR / "games.json"

# Colores y Estilos (Paleta Cyberpunk)
COLOR_BG = "#1e1e2e"        # Fondo principal oscuro
COLOR_SIDEBAR = "#181825"   # Fondo barra lateral
COLOR_ACCENT = "#cba6f7"    # Acento Púrpura
COLOR_ACCENT_2 = "#89b4fa"  # Acento Azul/Cian
COLOR_TEXT = "#cdd6f4"      # Texto principal
COLOR_INPUT_BG = "#313244"  # Fondo de inputs
COLOR_SUCCESS = "#a6e3a1"   # Verde éxito
COLOR_DANGER = "#f38ba8"    # Rojo peligro

# Crear directorio si no existe
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# GESTOR DE ESTILOS CSS (THEMING)
# ============================================================================
class StyleManager:
    @staticmethod
    def load_css():
        css = f"""
        /* --- GENERAL --- */
        window {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }}
        
        /* --- HEADER BAR --- */
        headerbar {{
            background-image: linear-gradient(to right, #11111b, #1e1e2e);
            border-bottom: 1px solid #45475a;
            min-height: 50px;
        }}
        headerbar label.title {{
            font-weight: 800;
            font-size: 16px;
            color: {COLOR_ACCENT};
            text-shadow: 0 0 10px rgba(203, 166, 247, 0.4);
        }}

        /* --- INPUTS & ENTRIES (Solución Texto Blanco) --- */
        entry {{
            background-color: {COLOR_INPUT_BG};
            color: #ffffff;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 8px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.2s;
        }}
        entry:focus {{
            border-color: {COLOR_ACCENT_2};
            box-shadow: 0 0 0 2px rgba(137, 180, 250, 0.3);
        }}
        entry selection {{
            background-color: {COLOR_ACCENT_2};
            color: #1e1e2e;
        }}

        /* --- SIDEBAR LIST --- */
        .sidebar {{
            background-color: {COLOR_SIDEBAR};
            border-right: 1px solid #313244;
        }}
        row {{
            padding: 12px;
            border-bottom: 1px solid #313244;
            transition: background 0.2s;
        }}
        row:selected {{
            background-color: #313244;
            border-left: 4px solid {COLOR_ACCENT};
        }}
        row label {{
            font-weight: bold;
        }}

        /* --- BOTONES 3D GAMING --- */
        button {{
            background-image: linear-gradient(to bottom, #45475a, #313244);
            color: white;
            border: none;
            border-radius: 6px;
            border-bottom: 3px solid #1e1e2e; /* Efecto 3D */
            padding: 8px 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-shadow: 0 1px 2px black;
            font-weight: bold;
        }}
        button:hover {{
            background-image: linear-gradient(to bottom, #585b70, #45475a);
            box-shadow: 0 5px 8px rgba(0,0,0,0.4);
        }}
        button:active {{
            border-bottom: 0px solid transparent;
            margin-top: 3px; /* Efecto presionar */
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
        }}
        
        button.suggested-action {{
            background-image: linear-gradient(to bottom, {COLOR_ACCENT_2}, #74c7ec);
            color: #1e1e2e;
            border-bottom-color: #558dc4;
            text-shadow: none;
        }}
        
        button.destructive-action {{
            background-image: linear-gradient(to bottom, {COLOR_DANGER}, #eba0ac);
            color: #1e1e2e;
            border-bottom-color: #9c4858;
            text-shadow: none;
        }}

        /* --- CARDS & PANELS --- */
        .card {{
            background-color: {COLOR_SIDEBAR};
            border-radius: 12px;
            border: 1px solid #45475a;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            padding: 20px;
        }}
        
        /* --- TEXT STYLES --- */
        .game-title {{
            font-size: 32px;
            font-weight: 900;
            color: {COLOR_ACCENT};
            letter-spacing: 1px;
        }}
        .game-subtitle {{
            font-size: 14px;
            color: #a6adc8;
        }}
        .emoji-icon {{
            font-size: 64px;
            text-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }}
        """
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

# ============================================================================
# LÓGICA DE NEGOCIO (MODEL)
# ============================================================================
class GamesManager:
    @staticmethod
    def load_games() -> List[Dict]:
        if GAMES_JSON.exists():
            try:
                with open(GAMES_JSON, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando JSON: {e}")
                return []
        return []

    @staticmethod
    def save_games(games: List[Dict]) -> bool:
        try:
            with open(GAMES_JSON, 'w', encoding='utf-8') as f:
                json.dump(games, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando JSON: {e}")
            return False

    @staticmethod
    def launch_game(game: Dict) -> bool:
        tipo = game.get("tipo", "appimage")
        ruta = game["ruta_ejecutable"]
        
        if not os.path.exists(ruta):
            return False
            
        try:
            if tipo == "appimage":
                subprocess.Popen([ruta])
            else: # binario
                directory = os.path.dirname(os.path.abspath(ruta))
                filename = os.path.basename(ruta)
                subprocess.Popen([f"./{filename}"], cwd=directory, shell=True)
            return True
        except Exception as e:
            print(f"Error launch: {e}")
            return False

# ============================================================================
# DIÁLOGO AGREGAR JUEGO (VIEW)
# ============================================================================
class GameDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Agregar Nuevo Juego", transient_for=parent, flags=0)
        self.set_default_size(500, 450)
        self.set_modal(True)
        
        # HeaderBar personalizada para el diálogo
        header = Gtk.HeaderBar(title="Agregar Juego")
        header.set_show_close_button(False)
        self.set_titlebar(header)
        
        # Botones de acción
        btn_cancel = Gtk.Button(label="Cancelar")
        btn_cancel.connect("clicked", lambda x: self.response(Gtk.ResponseType.CANCEL))
        header.pack_start(btn_cancel)
        
        btn_add = Gtk.Button(label="Guardar")
        btn_add.get_style_context().add_class("suggested-action")
        btn_add.connect("clicked", lambda x: self.response(Gtk.ResponseType.OK))
        header.pack_end(btn_add)

        # Contenido
        content_area = self.get_content_area()
        content_area.set_spacing(0)
        
        # Grid layout para formulario
        grid = Gtk.Grid(column_spacing=15, row_spacing=15)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        
        # Helpers para crear campos
        row = 0
        self.entries = {}
        
        def add_field(label_text, key, placeholder="", is_combo=False):
            nonlocal row
            lbl = Gtk.Label(label=label_text, xalign=0)
            lbl.get_style_context().add_class("dim-label")
            grid.attach(lbl, 0, row, 1, 1)
            
            if is_combo:
                widget = Gtk.ComboBoxText()
                widget.append("appimage", "AppImage (Portable)")
                widget.append("binario", "Binario (Carpeta Local)")
                widget.set_active(0)
                self.entries[key] = widget
            else:
                widget = Gtk.Entry()
                widget.set_placeholder_text(placeholder)
                self.entries[key] = widget
                
            grid.attach(widget, 1, row, 1, 1)
            row += 1

        add_field("Nombre:", "nombre", "Ej: Cyberpunk 2077")
        add_field("Categoría:", "categoria", "Ej: RPG, Acción")
        add_field("Descripción:", "descripcion", "Breve descripción...")
        add_field("Emoji/Icono:", "icono_emoji", "🎮")
        self.entries["icono_emoji"].set_max_length(2)
        add_field("Tipo:", "tipo", is_combo=True)
        
        # Selector de archivo especial
        lbl_ruta = Gtk.Label(label="Ejecutable:", xalign=0)
        grid.attach(lbl_ruta, 0, row, 1, 1)
        
        ruta_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.entries["ruta_ejecutable"] = Gtk.Entry()
        self.entries["ruta_ejecutable"].set_placeholder_text("/ruta/al/juego")
        ruta_box.pack_start(self.entries["ruta_ejecutable"], True, True, 0)
        
        btn_file = Gtk.Button(label="📂")
        btn_file.connect("clicked", self.on_file_clicked)
        ruta_box.pack_start(btn_file, False, False, 0)
        
        grid.attach(ruta_box, 1, row, 1, 1)
        
        content_area.pack_start(grid, True, True, 0)
        self.show_all()

    def on_file_clicked(self, widget):
        fc = Gtk.FileChooserDialog(
            title="Seleccionar Ejecutable",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        fc.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if fc.run() == Gtk.ResponseType.OK:
            self.entries["ruta_ejecutable"].set_text(fc.get_filename())
        fc.destroy()

    def get_data(self):
        return {
            "nombre": self.entries["nombre"].get_text(),
            "descripcion": self.entries["descripcion"].get_text(),
            "categoria": self.entries["categoria"].get_text(),
            "tipo": self.entries["tipo"].get_active_id(),
            "ruta_ejecutable": self.entries["ruta_ejecutable"].get_text(),
            "icono_emoji": self.entries["icono_emoji"].get_text() or "🎮"
        }

# ============================================================================
# VENTANA PRINCIPAL
# ============================================================================
class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=APP_NAME)
        self.set_icon_name("pixellauncher")
        self.set_default_size(1100, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.games = GamesManager.load_games()
        self.current_game_index = -1
        
        # 1. HeaderBar (Modern Title Bar)
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = APP_NAME
        header.props.subtitle = "Game Library Manager"
        self.set_titlebar(header)
        
        # Botón Agregar en el Header
        add_btn = Gtk.Button()
        add_icon = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        add_btn.add(add_icon)
        add_btn.get_style_context().add_class("suggested-action")
        add_btn.set_tooltip_text("Agregar nuevo juego")
        add_btn.connect("clicked", self.on_add_game)
        header.pack_start(add_btn)

        # 2. Layout Principal (Paned: Sidebar Izq | Contenido Der)
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned.set_position(300) # Ancho inicial sidebar
        self.add(self.paned)

        # --- Sidebar (Lista de juegos) ---
        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scroll.get_style_context().add_class("sidebar")
        
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-selected", self.on_row_selected)
        sidebar_scroll.add(self.listbox)
        
        self.paned.pack1(sidebar_scroll, resize=False, shrink=False)

        # --- Área de Detalles (Derecha) ---
        self.details_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.details_container.set_valign(Gtk.Align.CENTER)
        self.details_container.set_halign(Gtk.Align.CENTER)
        
        # Envolvemos el área de detalles en un scroll por si la ventana es pequeña
        details_scroll = Gtk.ScrolledWindow()
        details_scroll.add(self.details_container)
        self.paned.pack2(details_scroll, resize=True, shrink=False)

        # 3. Estado Inicial
        self.refresh_list()
        if self.games:
            self.listbox.select_row(self.listbox.get_row_at_index(0))
        else:
            self.show_empty_state()

    def refresh_list(self):
        """Recarga la lista lateral"""
        # Limpiar
        for child in self.listbox.get_children():
            self.listbox.remove(child)
        
        for game in self.games:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            # Emoji
            lbl_emoji = Gtk.Label(label=game.get("icono_emoji", "🎮"))
            row_box.pack_start(lbl_emoji, False, False, 0)
            
            # Textos
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            lbl_name = Gtk.Label(label=game["nombre"], xalign=0)
            lbl_cat = Gtk.Label(label=game.get("categoria", ""), xalign=0)
            lbl_cat.set_markup(f"<span size='small' foreground='#888'>{lbl_cat.get_text()}</span>")
            
            vbox.pack_start(lbl_name, True, True, 0)
            vbox.pack_start(lbl_cat, True, True, 0)
            row_box.pack_start(vbox, True, True, 0)
            
            row = Gtk.ListBoxRow()
            row.add(row_box)
            self.listbox.add(row)
        
        self.listbox.show_all()

    def show_empty_state(self):
        """Muestra mensaje si no hay juegos"""
        self.clear_details()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        icon = Gtk.Label()
        icon.set_markup("<span size='50000'>👾</span>")
        
        lbl = Gtk.Label(label="Tu biblioteca está vacía")
        lbl.get_style_context().add_class("game-title")
        
        sub = Gtk.Label(label="Haz clic en '+' arriba a la izquierda para empezar.")
        
        box.pack_start(icon, False, False, 0)
        box.pack_start(lbl, False, False, 0)
        box.pack_start(sub, False, False, 0)
        
        self.details_container.pack_start(box, True, True, 0)
        self.details_container.show_all()

    def clear_details(self):
        for child in self.details_container.get_children():
            self.details_container.remove(child)

    def on_row_selected(self, box, row):
        if row is not None:
            idx = row.get_index()
            self.current_game_index = idx
            self.show_game_details(self.games[idx])

    def show_game_details(self, game):
        self.clear_details()
        
        # Tarjeta contenedora
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        card.get_style_context().add_class("card")
        card.set_size_request(500, -1) # Ancho mínimo
        
        # 1. Icono Gigante
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        icon_box.set_size_request(-1, 150)
        lbl_icon = Gtk.Label()
        lbl_icon.set_markup(f"<span size='80000'>{game.get('icono_emoji', '🎮')}</span>")
        lbl_icon.get_style_context().add_class("emoji-icon")
        icon_box.pack_start(lbl_icon, True, True, 0)
        card.pack_start(icon_box, False, False, 0)
        
        # 2. Título y Metadata
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        lbl_title = Gtk.Label(label=game["nombre"])
        lbl_title.get_style_context().add_class("game-title")
        
        lbl_desc = Gtk.Label(label=game.get("descripcion", "Sin descripción"))
        lbl_desc.set_max_width_chars(40)
        lbl_desc.set_line_wrap(True)
        lbl_desc.set_justify(Gtk.Justification.CENTER)
        lbl_desc.get_style_context().add_class("game-subtitle")
        
        title_box.pack_start(lbl_title, False, False, 0)
        title_box.pack_start(lbl_desc, False, False, 0)
        card.pack_start(title_box, False, False, 10)
        
        # Separador visual
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        card.pack_start(sep, False, False, 10)
        
        # 3. Información Técnica
        grid_info = Gtk.Grid(column_spacing=20, row_spacing=10)
        grid_info.set_halign(Gtk.Align.CENTER)
        
        def add_info_row(label, value, row_idx):
            l = Gtk.Label(label=label, xalign=1)
            l.get_style_context().add_class("dim-label")
            v = Gtk.Label(label=value, xalign=0)
            v.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            v.set_max_width_chars(30)
            grid_info.attach(l, 0, row_idx, 1, 1)
            grid_info.attach(v, 1, row_idx, 1, 1)

        add_info_row("Categoría:", game.get("categoria", "-"), 0)
        add_info_row("Tipo:", game.get("tipo", "AppImage").capitalize(), 1)
        add_info_row("Ruta:", game["ruta_ejecutable"], 2)
        
        card.pack_start(grid_info, False, False, 10)
        
        # 4. Botones de Acción
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        action_box.set_halign(Gtk.Align.CENTER)
        action_box.set_margin_top(20)
        
        btn_launch = Gtk.Button(label="LANZAR JUEGO")
        btn_launch.get_style_context().add_class("suggested-action")
        btn_launch.set_size_request(200, 50)
        btn_launch.connect("clicked", lambda x: self.launch_current())
        
        btn_del = Gtk.Button(label="🗑 Eliminar")
        btn_del.get_style_context().add_class("destructive-action")
        btn_del.connect("clicked", lambda x: self.delete_current())
        
        action_box.pack_start(btn_launch, False, False, 0)
        action_box.pack_start(btn_del, False, False, 0)
        
        card.pack_start(action_box, False, False, 0)
        
        self.details_container.pack_start(card, False, False, 0)
        self.details_container.show_all()

    def on_add_game(self, widget):
        dialog = GameDialog(self)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            if data["nombre"] and data["ruta_ejecutable"]:
                self.games.append(data)
                GamesManager.save_games(self.games)
                self.refresh_list()
                # Seleccionar el nuevo
                row = self.listbox.get_row_at_index(len(self.games) - 1)
                self.listbox.select_row(row)
        
        dialog.destroy()

    def launch_current(self):
        if 0 <= self.current_game_index < len(self.games):
            game = self.games[self.current_game_index]
            success = GamesManager.launch_game(game)
            if not success:
                msg = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.ERROR,
                                      buttons=Gtk.ButtonsType.OK, text="Error al lanzar")
                msg.format_secondary_text(f"No se pudo encontrar o ejecutar:\n{game['ruta_ejecutable']}")
                msg.run()
                msg.destroy()

    def delete_current(self):
        if 0 <= self.current_game_index < len(self.games):
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="¿Eliminar juego?"
            )
            dialog.format_secondary_text("Esta acción eliminará el juego de la lista (no del disco).")
            if dialog.run() == Gtk.ResponseType.YES:
                self.games.pop(self.current_game_index)
                GamesManager.save_games(self.games)
                self.refresh_list()
                if not self.games:
                    self.show_empty_state()
                else:
                    # Seleccionar el anterior o el primero
                    new_idx = max(0, self.current_game_index - 1)
                    self.listbox.select_row(self.listbox.get_row_at_index(new_idx))
            dialog.destroy()

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    StyleManager.load_css()
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
