#!/usr/bin/env python3
"""
PromptVault Pro 2.0 - Main Application
Complete implementation with all UI components
"""

import json
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.scrolledtext as st
from typing import Optional, Dict, Any, Tuple
from collections import defaultdict

from psychological_engine import PsychologicalOrchestrator, ConfigLoader


class PromptVaultApp:
    """Main application controller with complete UI implementation."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_app()
        self.psych_orchestrator = PsychologicalOrchestrator()
        self.setup_ui()
        self.start_background_monitors()

    def setup_app(self) -> None:
        """Initialize application settings and data."""
        self.root.title("PromptVault Pro 2.0 🧠⚡")
        self.root.geometry("1000x800")
        self.root.configure(bg='#2b2b2b')
        
        self.data_file = "prompts.json"
        self.prompts = self.load_data()
        self.current_category = "General"
        self.current_prompt: Optional[str] = None
        self.pomodoro_active = False
        self.pomodoro_start: Optional[float] = None
        self.pomodoro_duration = 25 * 60

    def setup_styles(self) -> None:
        """Configure modern, dark theme styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.base_bg = '#2b2b2b'
        self.base_fg = '#ffffff'
        self.base_accent = '#4CAF50'
        
        self.style.configure('TFrame', background=self.base_bg)
        self.style.configure('TLabel', background=self.base_bg, foreground=self.base_fg, 
                           font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 9), padding=6)
        self.style.configure('Accent.TButton', background=self.base_accent, foreground='white')
        self.style.configure('Treeview', background='#3c3c3c', fieldbackground='#3c3c3c', 
                           foreground=self.base_fg, font=('Segoe UI', 9))
        self.style.configure('Treeview.Heading', background='#404040', foreground=self.base_fg, 
                           font=('Segoe UI', 10, 'bold'))

    def setup_ui(self) -> None:
        """Build the complete user interface."""
        self.setup_styles()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_header(main_frame)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_left_sidebar(content_frame)
        self.setup_enhanced_editor(content_frame)
        self.setup_insights_panel(main_frame)
        
        self.refresh_all()

    def setup_header(self, parent: ttk.Frame) -> None:
        """Setup application header with status indicators."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="PromptVault Pro 2.0", 
                 font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        
        self.psych_status = ttk.Label(header_frame, text="🧠 Psychology: OFF", 
                                     font=('Segoe UI', 10))
        self.psych_status.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(header_frame, text="⚙️ Psychology Settings", 
                  command=self.show_psych_settings).pack(side=tk.RIGHT)
        
        self.pomodoro_label = ttk.Label(header_frame, text="🍅 25:00", 
                                       font=('Segoe UI', 10))
        self.pomodoro_label.pack(side=tk.RIGHT, padx=(0, 10))

    def setup_left_sidebar(self, parent: ttk.Frame) -> None:
        """Setup categories and prompts sidebar."""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.setup_categories_section(left_frame)
        self.setup_prompts_section(left_frame)

    def setup_categories_section(self, parent: ttk.Frame) -> None:
        """Setup categories management section."""
        cat_frame = ttk.LabelFrame(parent, text="📁 Categories", padding=10)
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cat_listbox = tk.Listbox(cat_frame, bg='#3c3c3c', fg='white', 
                                     font=('Segoe UI', 10), selectbackground=self.base_accent, height=8)
        self.cat_listbox.pack(fill=tk.X)
        self.cat_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        cat_controls = ttk.Frame(cat_frame)
        cat_controls.pack(fill=tk.X, pady=(5, 0))
        
        self.cat_entry = ttk.Entry(cat_controls, font=('Segoe UI', 9))
        self.cat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.cat_entry.bind('<Return>', self.add_category)
        
        ttk.Button(cat_controls, text="+", width=3, command=self.add_category).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(cat_controls, text="−", width=3, command=self.remove_category).pack(side=tk.RIGHT, padx=(2, 0))

    def setup_prompts_section(self, parent: ttk.Frame) -> None:
        """Setup prompts management section."""
        prompts_frame = ttk.LabelFrame(parent, text="📝 Prompts", padding=10)
        prompts_frame.pack(fill=tk.BOTH, expand=True)
        
        self.prompts_tree = ttk.Treeview(prompts_frame, columns=('title',), show='tree', height=15)
        self.prompts_tree.heading('#0', text='Prompts')
        self.prompts_tree.column('#0', width=200)
        self.prompts_tree.bind('<<TreeviewSelect>>', self.on_prompt_select)
        
        scrollbar = ttk.Scrollbar(prompts_frame, orient=tk.VERTICAL, command=self.prompts_tree.yview)
        self.prompts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.prompts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        prompt_controls = ttk.Frame(prompts_frame)
        prompt_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(prompt_controls, text="New Prompt", command=self.new_prompt).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(prompt_controls, text="Delete Prompt", command=self.delete_prompt).pack(side=tk.LEFT)

    def setup_enhanced_editor(self, parent: ttk.Frame) -> None:
        """Setup enhanced editor with psychological features."""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        editor_frame = ttk.LabelFrame(right_frame, text="✍️ Enhanced Editor", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_editor_indicators(editor_frame)
        self.setup_title_input(editor_frame)
        self.setup_content_editor(editor_frame)
        self.setup_action_buttons(editor_frame)

    def setup_editor_indicators(self, parent: ttk.Frame) -> None:
        """Setup emotional and cognitive indicators."""
        tone_frame = ttk.Frame(parent)
        tone_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tone_frame, text="Detected Tone:").pack(side=tk.LEFT)
        self.tone_indicator = ttk.Label(tone_frame, text="neutral", foreground=self.base_accent, 
                                      font=('Segoe UI', 9, 'bold'))
        self.tone_indicator.pack(side=tk.LEFT, padx=(5, 0))
        
        self.load_indicator = ttk.Progressbar(tone_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.load_indicator.pack(side=tk.RIGHT)
        ttk.Label(tone_frame, text="Complexity:").pack(side=tk.RIGHT, padx=(0, 5))

    def setup_title_input(self, parent: ttk.Frame) -> None:
        """Setup title input field."""
        ttk.Label(parent, text="Title:").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(parent, font=('Segoe UI', 11))
        self.title_entry.pack(fill=tk.X, pady=(2, 10))
        self.title_entry.bind('<KeyRelease>', self.on_content_change)

    def setup_content_editor(self, parent: ttk.Frame) -> None:
        """Setup content editor text area."""
        ttk.Label(parent, text="Content:").pack(anchor=tk.W)
        
        self.content_text = st.ScrolledText(parent, wrap=tk.WORD, bg='#3c3c3c', fg='white', 
                                          insertbackground='white', font=('Consolas', 10), 
                                          padx=10, pady=10, height=12)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(2, 10))
        self.content_text.bind('<KeyRelease>', self.on_content_change)

    def setup_action_buttons(self, parent: ttk.Frame) -> None:
        """Setup editor action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 Save Prompt", style='Accent.TButton', 
                  command=self.save_prompt).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧠 Enhance Prompt", 
                  command=self.enhance_current_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🍅 Start Focus", 
                  command=self.toggle_pomodoro).pack(side=tk.LEFT, padx=5)
        
        # Import/Export buttons
        io_frame = ttk.Frame(parent)
        io_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(io_frame, text="📤 Export Database", 
                  command=self.export_database).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(io_frame, text="📥 Import Database", 
                  command=self.import_database).pack(side=tk.LEFT)

    def setup_insights_panel(self, parent: ttk.Frame) -> None:
        """Setup psychological insights panel."""
        insights_frame = ttk.LabelFrame(parent, text="🧠 Psychological Insights", padding=10)
        insights_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.insights_text = st.ScrolledText(insights_frame, wrap=tk.WORD, bg='#3c3c3c', fg='white',
                                           font=('Segoe UI', 9), height=4, padx=10, pady=10)
        self.insights_text.pack(fill=tk.BOTH, expand=True)
        self.insights_text.config(state=tk.DISABLED)
        
        self.update_insights_display()

    def show_psych_settings(self) -> None:
        """Show psychological features settings dialog."""
        settings = tk.Toplevel(self.root)
        settings.title("Psychological Scaffolding Settings")
        settings.geometry("500x500")
        settings.configure(bg=self.base_bg)
        settings.transient(self.root)
        settings.grab_set()
        
        main_frame = ttk.Frame(settings)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Psychological Features", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Feature toggles
        emotional_var = tk.BooleanVar(value=self.psych_orchestrator.psych_scaffolding.enabled_features['emotional'])
        cognitive_var = tk.BooleanVar(value=self.psych_orchestrator.psych_scaffolding.enabled_features['cognitive'])
        behavioral_var = tk.BooleanVar(value=self.psych_orchestrator.psych_scaffolding.enabled_features['behavioral'])
        
        ttk.Checkbutton(main_frame, text="🎭 Emotional Resonance Engine", 
                       variable=emotional_var).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="🧠 Cognitive Flow Optimizer", 
                       variable=cognitive_var).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="📊 Behavioral Nudge System", 
                       variable=behavioral_var).pack(anchor=tk.W, pady=5)
        
        # Stealth techniques section
        ttk.Label(main_frame, text="Stealth Enhancement Techniques", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))
        
        stealth_vars = {}
        for technique in self.psych_orchestrator.stealth_engine.techniques_enabled:
            var = tk.BooleanVar(value=self.psych_orchestrator.stealth_engine.techniques_enabled[technique])
            stealth_vars[technique] = var
            display_name = technique.replace('_', ' ').title()
            ttk.Checkbutton(main_frame, text=f"🜂 {display_name}", 
                           variable=var).pack(anchor=tk.W, pady=2)
        
        ttk.Label(main_frame, text="Note: All processing happens locally on your device.\nNo data is sent to external servers.",
                 font=('Segoe UI', 8), foreground='#888').pack(pady=10)
        
        def apply_settings():
            # Apply psychological features
            self.psych_orchestrator.psych_scaffolding.enabled_features.update({
                'emotional': emotional_var.get(),
                'cognitive': cognitive_var.get(),
                'behavioral': behavioral_var.get()
            })
            
            # Apply stealth techniques
            for technique, var in stealth_vars.items():
                self.psych_orchestrator.stealth_engine.techniques_enabled[technique] = var.get()
            
            self.update_psych_status()
            settings.destroy()
            
        ttk.Button(main_frame, text="Apply Settings", command=apply_settings).pack(pady=10)

    def update_psych_status(self) -> None:
        """Update psychological status indicator."""
        enabled_count = sum(self.psych_orchestrator.psych_scaffolding.enabled_features.values())
        if enabled_count == 0:
            self.psych_status.config(text="🧠 Psychology: OFF")
        else:
            self.psych_status.config(text=f"🧠 Psychology: {enabled_count}/3 ON")

    def on_content_change(self, event=None) -> None:
        """Handle content changes for psychological analysis."""
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            return
            
        analysis = self.psych_orchestrator.analyze_content(content)
        self.tone_indicator.config(text=analysis['emotional_tone'])
        self.load_indicator['value'] = analysis['cognitive_load'] * 100
        
        self.psych_orchestrator.track_activity("edit", {
            'category': self.current_category,
            'content_length': len(content)
        })

    def enhance_current_prompt(self) -> None:
        """Apply stealth enhancement to current prompt."""
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Content", "Please enter some prompt content first.")
            return
            
        enhanced_content, report = self.psych_orchestrator.enhance_prompt(content)
        self.show_enhancement_results(enhanced_content, report)

    def show_enhancement_results(self, enhanced_content: str, report: Dict[str, Any]) -> None:
        """Show enhancement results in a dialog."""
        results_window = tk.Toplevel(self.root)
        results_window.title("Prompt Enhancement Results")
        results_window.geometry("800x600")
        results_window.configure(bg=self.base_bg)
        results_window.transient(self.root)
        results_window.grab_set()
        
        main_frame = ttk.Frame(results_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Enhanced Prompt", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
        
        enhanced_text = st.ScrolledText(main_frame, wrap=tk.WORD, bg='#3c3c3c', fg='white',
                                      font=('Consolas', 10), height=12)
        enhanced_text.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        enhanced_text.insert(1.0, enhanced_content)
        
        # Report display
        ttk.Label(main_frame, text="Enhancement Report", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
        
        report_text = st.ScrolledText(main_frame, wrap=tk.WORD, bg='#3c3c3c', fg='white',
                                    font=('Consolas', 9), height=8)
        report_text.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        report_text.insert(1.0, json.dumps(report, indent=2))
        report_text.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def use_enhanced() -> None:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, enhanced_content)
            results_window.destroy()
            
        ttk.Button(button_frame, text="Use Enhanced Prompt", 
                  command=use_enhanced).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", 
                  command=results_window.destroy).pack(side=tk.LEFT)

    def toggle_pomodoro(self) -> None:
        """Toggle Pomodoro focus timer."""
        if not self.pomodoro_active:
            self.pomodoro_active = True
            self.pomodoro_start = time.time()
            self.pomodoro_label.config(text="🍅 25:00")
            self.update_pomodoro()
            messagebox.showinfo("Focus Session", "25-minute focus session started! 🍅")
        else:
            self.pomodoro_active = False
            self.pomodoro_label.config(text="🍅 25:00")
            messagebox.showinfo("Focus Session", "Focus session ended. Take a break! ⏸️")

    def update_pomodoro(self) -> None:
        """Update Pomodoro timer display."""
        if self.pomodoro_active:
            elapsed = time.time() - self.pomodoro_start
            remaining = max(0, self.pomodoro_duration - elapsed)
            
            if remaining <= 0:
                self.pomodoro_active = False
                self.pomodoro_label.config(text="🍅 25:00")
                messagebox.showinfo("Time's Up!", "Focus session complete! Take a 5-minute break. 🎉")
                return
                
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            self.pomodoro_label.config(text=f"🍅 {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_pomodoro)

    def update_insights_display(self) -> None:
        """Update psychological insights display."""
        if not any(self.psych_orchestrator.psych_scaffolding.enabled_features.values()):
            self.insights_text.config(state=tk.NORMAL)
            self.insights_text.delete(1.0, tk.END)
            self.insights_text.insert(1.0, "💡 Enable psychological features in settings to see insights.")
            self.insights_text.config(state=tk.DISABLED)
            self.root.after(30000, self.update_insights_display)
            return
            
        # Simple insights based on usage patterns
        recent_sessions = [t for t in self.psych_orchestrator.psych_scaffolding.usage_patterns['session_start_times'] 
                          if time.time() - t < 86400]  # Last 24 hours
        
        if len(recent_sessions) > 5:
            insight = "🌅 You're most active today! Great momentum."
        elif self.psych_orchestrator.psych_scaffolding.usage_patterns['category_usage']:
            top_category = max(self.psych_orchestrator.psych_scaffolding.usage_patterns['category_usage'].items(), 
                             key=lambda x: x[1])
            insight = f"📊 You frequently work in '{top_category[0]}' category."
        else:
            insight = "💡 Start creating prompts to see personalized insights."
            
        self.insights_text.config(state=tk.NORMAL)
        self.insights_text.delete(1.0, tk.END)
        self.insights_text.insert(1.0, f"Insight: {insight}")
        self.insights_text.config(state=tk.DISABLED)
        
        # Schedule next update
        self.root.after(30000, self.update_insights_display)

    def start_background_monitors(self) -> None:
        """Start background psychological monitoring."""
        self.root.after(60000, self.check_for_interventions)

    def check_for_interventions(self) -> None:
        """Check if psychological intervention is needed."""
        if self.psych_orchestrator.should_intervene():
            if messagebox.askyesno("Take a Breath?", 
                                 "You've been editing rapidly. Would you like to take a 30-second break?"):
                self.root.after(30000, lambda: messagebox.showinfo("Welcome Back", 
                                                                 "Ready to continue? 💫"))
        self.root.after(60000, self.check_for_interventions)

    # Core data management methods
    def load_data(self) -> Dict[str, Any]:
        """Load prompts data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"categories": {"General": {}}}
        return {"categories": {"General": {}}}

    def save_data(self) -> bool:
        """Save prompts data to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            return False

    def refresh_categories(self) -> None:
        """Refresh categories listbox."""
        self.cat_listbox.delete(0, tk.END)
        for category in self.prompts["categories"]:
            self.cat_listbox.insert(tk.END, category)
        
        if self.current_category in self.prompts["categories"]:
            index = list(self.prompts["categories"].keys()).index(self.current_category)
            self.cat_listbox.selection_set(index)

    def refresh_prompts_list(self) -> None:
        """Refresh prompts treeview for current category."""
        self.prompts_tree.delete(*self.prompts_tree.get_children())
        
        if self.current_category in self.prompts["categories"]:
            category_prompts = self.prompts["categories"][self.current_category]
            for prompt_id, prompt_data in category_prompts.items():
                self.prompts_tree.insert('', tk.END, iid=prompt_id, text=prompt_data["title"])

    def refresh_all(self) -> None:
        """Refresh all UI elements."""
        self.refresh_categories()
        self.refresh_prompts_list()
        self.update_insights_display()

    def on_category_select(self, event=None) -> None:
        """Handle category selection."""
        selection = self.cat_listbox.curselection()
        if selection:
            self.current_category = self.cat_listbox.get(selection[0])
            self.refresh_prompts_list()
            self.clear_editor()

    def on_prompt_select(self, event=None) -> None:
        """Handle prompt selection."""
        selection = self.prompts_tree.selection()
        if selection and self.current_category in self.prompts["categories"]:
            prompt_id = selection[0]
            category_prompts = self.prompts["categories"][self.current_category]
            if prompt_id in category_prompts:
                self.current_prompt = prompt_id
                prompt_data = category_prompts[prompt_id]
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, prompt_data["title"])
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(1.0, prompt_data["content"])
                self.on_content_change()

    def add_category(self, event=None) -> None:
        """Add a new category."""
        category_name = self.cat_entry.get().strip()
        if category_name and category_name not in self.prompts["categories"]:
            self.prompts["categories"][category_name] = {}
            self.cat_entry.delete(0, tk.END)
            if self.save_data():
                self.refresh_categories()
                messagebox.showinfo("Success", f"Category '{category_name}' added!")
            else:
                self.prompts["categories"].pop(category_name)

    def remove_category(self) -> None:
        """Remove selected category."""
        selection = self.cat_listbox.curselection()
        if selection:
            category_name = self.cat_listbox.get(selection[0])
            if category_name == "General":
                messagebox.showwarning("Warning", "Cannot delete the 'General' category!")
                return
                
            if messagebox.askyesno("Confirm", f"Delete category '{category_name}' and all its prompts?"):
                self.prompts["categories"].pop(category_name)
                if self.save_data():
                    self.current_category = "General"
                    self.refresh_categories()
                    self.refresh_prompts_list()
                    self.clear_editor()

    def new_prompt(self) -> None:
        """Create a new prompt."""
        if not self.current_category:
            messagebox.showwarning("Warning", "Please select a category first!")
            return
            
        self.clear_editor()
        self.title_entry.focus()

    def save_prompt(self) -> None:
        """Save current prompt."""
        title = self.title_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title or not content:
            messagebox.showwarning("Warning", "Please enter both title and content!")
            return
            
        if not self.current_category:
            messagebox.showwarning("Warning", "Please select a category first!")
            return
        
        prompt_id = self.current_prompt or "prompt_" + str(abs(hash(title)))[:8]
        
        if self.current_category not in self.prompts["categories"]:
            self.prompts["categories"][self.current_category] = {}
            
        self.prompts["categories"][self.current_category][prompt_id] = {
            "title": title,
            "content": content,
            "category": self.current_category,
            "last_modified": time.time()
        }
        
        if self.save_data():
            self.refresh_prompts_list()
            messagebox.showinfo("Success", "Prompt saved successfully!")

    def delete_prompt(self) -> None:
        """Delete selected prompt."""
        selection = self.prompts_tree.selection()
        if selection and self.current_category in self.prompts["categories"]:
            prompt_id = selection[0]
            prompt_title = self.prompts["categories"][self.current_category][prompt_id]["title"]
            
            if messagebox.askyesno("Confirm", f"Delete prompt '{prompt_title}'?"):
                self.prompts["categories"][self.current_category].pop(prompt_id)
                if self.save_data():
                    self.refresh_prompts_list()
                    self.clear_editor()

    def copy_to_clipboard(self) -> None:
        """Copy current prompt content to clipboard."""
        content = self.content_text.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Prompt copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No content to copy!")

    def clear_editor(self) -> None:
        """Clear the editor fields."""
        self.current_prompt = None
        self.title_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.tone_indicator.config(text="neutral")
        self.load_indicator['value'] = 0

    def export_database(self) -> None:
        """Export entire database to JSON file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Prompt Database"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.prompts, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Database exported to {filename}!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def import_database(self) -> None:
        """Import database from JSON file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Prompt Database"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                
                if "categories" in imported_data and isinstance(imported_data["categories"], dict):
                    if messagebox.askyesno("Confirm", "This will replace your current database. Continue?"):
                        self.prompts = imported_data
                        if self.save_data():
                            self.current_category = "General"
                            self.refresh_all()
                            self.clear_editor()
                            messagebox.showinfo("Success", "Database imported successfully!")
                else:
                    messagebox.showerror("Error", "Invalid database format!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")


def main():
    """Main application entry point."""
    root = tk.Tk()
    app = PromptVaultApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
