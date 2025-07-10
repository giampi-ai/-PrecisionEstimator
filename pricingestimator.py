import ttkbootstrap as tb
from ttkbootstrap.constants import *
import json
from tkinter import messagebox, filedialog
from fpdf import FPDF
import tkinter as tk  # Add this import for tk.Listbox

# Pricing dictionary (LF = linear foot, sqft = square feet)
pricing = {
    "Flooring and Tile": {
        "Flooring install LVP (sqft)": (4, 7),
        "Flooring install LVT (sqft)": (2.5, 3.5),
        "Flooring install laminate (sqft)": (2.5, 4.5),
        "Flooring install hardwood (sqft)": (4, 8),
        "Tile install (sqft)": (6, 6),
        "Backsplash install (sqft)": (15, 25),
        "Backsplash install angle (sqft)": (20, 35),
        "Carpet removal (sqft)": (1, 1),
        "Laminate floor removal (sqft)": (0.75, 2),
        "Tile removal (sqft)": (4, 4),
        "Subfloor install (sqft)": (2, 2),
    },
    "Drywall": {
        "Drywall install (remove & replace) (sqft)": (2.5, 2.5),
        "Drywall install (new construction) (per sheet)": (60, 60),
        "Minor drywall repairs (per hour)": (25, 25),
        "Drywall patches small (sqft)": (2.5, 5),
        "Drywall patches medium to large (sqft)": (3.5, 5),
    },
    "Trim": {
        "Window trim (LF)": (4, 8),
        "Door trim (LF)": (3, 7),
        "Ceiling trim (LF)": (3, 7),
        "Crown molding (LF)": (5, 8),
        "Baseboard (LF)": (1.5, 3.5),
        "Quarter round (LF)": (1, 3),
    },
    "Paint and Stain": {
        "Paint wall (sqft)": (2.5, 3.5),
        "Paint ceiling (sqft)": (1, 2.5),
        "Paint trim (LF)": (1, 3),
        "Painting interior doors (per door)": (45, 45),
    },
    "Framing": {
        "Interior framing (sqft)": (7, 16),
    },
    "Insulation": {
        "Insulation install (sqft)": (1, 1),
    },
    "Sheathing": {
        "Sheathing install (sqft)": (1, 3),
    },
    "Sealing Services": {
        "Sealing tile (sqft)": (1, 3),
        "Sealing countertops standard sizes (per job)": (100, 200),
        "Sealing countertops small sizes (per job)": (50, 100),
        "Sealing driveways (sqft)": (0.20, 0.20),
    }
}

class PriceEstimatorApp:
    def __init__(self, root):
        # --- Variable Initialization ---
        self.client_name_var = tb.StringVar()
        self.client_address_var = tb.StringVar()
        self.client_phone_var = tb.StringVar()
        self.client_email_var = tb.StringVar()
        self.category_var = tb.StringVar()
        self.service_var = tb.StringVar()
        self.quantity_var = tb.StringVar()
        self.unit_var = tb.StringVar(value="sqft")
        self.services_list = []

        self.root = root
        self.root.title("Precision Build Pros - Price Estimator")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        self.root.option_add("*Font", "Arial 11")

        # Main container frame using grid
        self.main_frame = tb.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # --- Header ---
        self.header = tb.Label(self.main_frame, text="Precision Build Pros - Price Estimator", font=("Arial", 18, "bold"), bootstyle="primary", anchor="center")
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(18, 8), padx=18)

        # --- Client Info ---
        self.client_frame = tb.Labelframe(self.main_frame, text="Client Information", bootstyle="primary")
        self.client_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8), ipadx=8, ipady=8)
        self.client_frame.columnconfigure(1, weight=1)
        self.client_frame.columnconfigure(3, weight=1)
        tb.Label(self.client_frame, text="Name:").grid(column=0, row=0, sticky="w", padx=5, pady=2)
        tb.Entry(self.client_frame, textvariable=self.client_name_var, width=30).grid(column=1, row=0, sticky="ew", padx=5, pady=2)
        tb.Label(self.client_frame, text="Address:").grid(column=0, row=1, sticky="w", padx=5, pady=2)
        tb.Entry(self.client_frame, textvariable=self.client_address_var, width=30).grid(column=1, row=1, sticky="ew", padx=5, pady=2)
        tb.Label(self.client_frame, text="Phone:").grid(column=2, row=0, sticky="w", padx=5, pady=2)
        tb.Entry(self.client_frame, textvariable=self.client_phone_var, width=20).grid(column=3, row=0, sticky="ew", padx=5, pady=2)
        tb.Label(self.client_frame, text="Email:").grid(column=2, row=1, sticky="w", padx=5, pady=2)
        tb.Entry(self.client_frame, textvariable=self.client_email_var, width=20).grid(column=3, row=1, sticky="ew", padx=5, pady=2)

        # --- Service Entry ---
        self.service_frame = tb.Labelframe(self.main_frame, text="Add Service", bootstyle="info")
        self.service_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8), ipadx=8, ipady=8)
        self.service_frame.columnconfigure(1, weight=1)
        tb.Label(self.service_frame, text="Category:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.category_cb = tb.Combobox(self.service_frame, textvariable=self.category_var, values=list(pricing.keys()), state="readonly")
        self.category_cb.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.category_cb.bind("<<ComboboxSelected>>", self.update_services)
        tb.Label(self.service_frame, text="Service:").grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.service_cb = tb.Combobox(self.service_frame, textvariable=self.service_var, state="readonly")
        self.service_cb.grid(column=1, row=1, padx=5, pady=5, sticky="ew")
        self.service_cb.bind("<<ComboboxSelected>>", self.update_unit_options)
        tb.Label(self.service_frame, text="Quantity:").grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.quantity_entry = tb.Entry(self.service_frame, textvariable=self.quantity_var)
        self.quantity_entry.grid(column=1, row=2, padx=5, pady=5, sticky="ew")
        tb.Label(self.service_frame, text="Unit:").grid(column=2, row=2, padx=5, pady=5, sticky="w")
        self.unit_cb = tb.Combobox(self.service_frame, textvariable=self.unit_var, values=["sqft", "LF"], state="readonly", width=6)
        self.unit_cb.grid(column=3, row=2, padx=5, pady=5, sticky="w")
        self.add_service_btn = tb.Button(self.service_frame, text="Add Service to Estimate", bootstyle="success", command=self.add_service)
        self.add_service_btn.grid(column=1, row=3, padx=5, pady=10, sticky="ew")

        # --- Services List (Scrollable) ---
        try:
            from ttkbootstrap.scrolled import ScrolledFrame
            self.scrolled = ScrolledFrame
        except ImportError:
            self.scrolled = None
        self.list_frame = tb.Labelframe(self.main_frame, text="Services in Estimate", bootstyle="secondary")
        self.list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=18, pady=(0, 8), ipadx=8, ipady=8)
        self.main_frame.rowconfigure(3, weight=2)
        self.list_frame.rowconfigure(0, weight=1)
        self.list_frame.columnconfigure(0, weight=1)
        if self.scrolled:
            self.scrolled_frame = self.scrolled(self.list_frame, autohide=True, bootstyle="info")
            self.scrolled_frame.grid(row=0, column=0, sticky="nsew")
            self.services_listbox = tk.Listbox(self.scrolled_frame, height=8, width=80, font="Arial 11", relief="flat", borderwidth=0, highlightthickness=0)
            self.services_listbox.pack(fill="both", expand=True, padx=2, pady=2)
        else:
            self.services_listbox = tk.Listbox(self.list_frame, height=8, width=80, font="Arial 11", relief="flat", borderwidth=0, highlightthickness=0)
            self.services_listbox.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.remove_service_btn = tb.Button(self.list_frame, text="Remove Selected Service", bootstyle="danger", command=self.remove_service)
        self.remove_service_btn.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # --- Actions ---
        self.actions_frame = tb.Frame(self.main_frame)
        self.actions_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8))
        self.actions_frame.columnconfigure((0,1,2,3), weight=1)
        try:
            from ttkbootstrap.icons import Icon
            self.export_pdf_icon = Icon("file-earmark-arrow-down").image
            self.save_json_icon = Icon("save").image
            self.load_json_icon = Icon("folder2-open").image
            self.clear_icon = Icon("x-circle").image
            self.export_pdf_btn = tb.Button(self.actions_frame, text=" Export to PDF", bootstyle="outline", command=self.export_to_pdf, image=self.export_pdf_icon, compound="left")
            self.save_json_btn = tb.Button(self.actions_frame, text=" Save Estimate", bootstyle="outline", command=self.save_estimate, image=self.save_json_icon, compound="left")
            self.load_json_btn = tb.Button(self.actions_frame, text=" Load Estimate", bootstyle="outline", command=self.load_estimate, image=self.load_json_icon, compound="left")
            self.clear_btn = tb.Button(self.actions_frame, text=" Clear All", bootstyle="outline", command=self.clear_all, image=self.clear_icon, compound="left")
        except Exception:
            self.export_pdf_btn = tb.Button(self.actions_frame, text="Export to PDF", bootstyle="outline", command=self.export_to_pdf)
            self.save_json_btn = tb.Button(self.actions_frame, text="Save Estimate", bootstyle="outline", command=self.save_estimate)
            self.load_json_btn = tb.Button(self.actions_frame, text="Load Estimate", bootstyle="outline", command=self.load_estimate)
            self.clear_btn = tb.Button(self.actions_frame, text="Clear All", bootstyle="outline", command=self.clear_all)
        self.export_pdf_btn.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
        self.save_json_btn.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.load_json_btn.grid(column=2, row=0, padx=5, pady=5, sticky="ew")
        self.clear_btn.grid(column=3, row=0, padx=5, pady=5, sticky="ew")

        # --- Result Label ---
        self.result_label = tb.Label(self.main_frame, text="", font=("Arial", 12, "bold"), bootstyle="primary")
        self.result_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 0))

        # --- Footer/Total Bar (Pinned) ---
        self.footer = tb.Frame(self.root, bootstyle="secondary")
        self.footer.grid(row=1, column=0, sticky="ew")
        self.root.rowconfigure(1, weight=0)
        self.total_label = tb.Label(self.footer, text="Total: $0.00", font=("Arial", 16, "bold"), bootstyle="success", anchor="e", justify="right", padding=(12, 8))
        self.total_label.pack(fill="x", padx=0, pady=0)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Make sure the main frame expands, footer stays pinned
        self.root.update_idletasks()
        self.root.minsize(700, 600)

    def update_services(self, event=None):
        selected_category = self.category_var.get()
        if selected_category in pricing:
            services = list(pricing[selected_category].keys())
            self.service_cb['values'] = services
            self.service_cb.set('')
        self.update_unit_options()

    def update_unit_options(self, event=None):
        # For Drywall, only allow 'sqft'. For others, allow both.
        if self.category_var.get() == "Drywall":
            self.unit_cb['values'] = ["sqft"]
            self.unit_var.set("sqft")
            self.unit_cb.config(state="readonly")
        else:
            self.unit_cb['values'] = ["sqft", "LF"]
            if self.unit_var.get() not in ["sqft", "LF"]:
                self.unit_var.set("sqft")
            self.unit_cb.config(state="readonly")

    def add_service(self):
        category = self.category_var.get()
        service = self.service_var.get()
        quantity = self.quantity_var.get()
        unit = self.unit_var.get()
        errors = []
        if not category:
            errors.append("Category is required.")
        if not service:
            errors.append("Service is required.")
        if not quantity:
            errors.append("Quantity is required.")
        else:
            try:
                q = float(quantity)
                if q <= 0:
                    errors.append("Quantity must be greater than zero.")
            except ValueError:
                errors.append("Quantity must be a number.")
        if category and service and service not in pricing.get(category, {}):
            errors.append("Selected service is not valid for the chosen category.")
        if category == "Drywall" and unit != "sqft":
            errors.append("Drywall services must use 'sqft' as the unit.")
        if category != "Drywall" and service and unit not in service:
            errors.append(f"Unit '{unit}' may not match the selected service.")
        if errors:
            messagebox.showerror("Input Error", "\n".join(errors))
            return
        try:
            quantity = float(quantity)
            price_range = pricing[category][service]
            average_price = sum(price_range) / 2
            # Special handling for drywall install services
            if category == "Drywall" and "install" in service.lower():
                import math
                num_sheets = math.ceil(quantity / 32)
                estimated_cost = num_sheets * average_price
                service_entry = {
                    "category": category,
                    "service": service,
                    "quantity": quantity,
                    "unit": unit,
                    "average_price": average_price,
                    "estimated_cost": estimated_cost,
                    "num_sheets": num_sheets
                }
            else:
                estimated_cost = quantity * average_price
                service_entry = {
                    "category": category,
                    "service": service,
                    "quantity": quantity,
                    "unit": unit,
                    "average_price": average_price,
                    "estimated_cost": estimated_cost
                }
            self.services_list.append(service_entry)
            self.update_services_listbox()
            self.result_label.config(text="Service added. Add more or export/save estimate.")
            self.update_total_label()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def update_services_listbox(self):
        self.services_listbox.delete(0, "end")
        for idx, s in enumerate(self.services_list, 1):
            if s.get("num_sheets"):
                self.services_listbox.insert("end", f"{idx}. {s['category']} - {s['service']} | {s['quantity']} sqft ({s['num_sheets']} sheets) | Rate: ${s['average_price']:.2f} | Subtotal: ${s['estimated_cost']:.2f}")
            else:
                self.services_listbox.insert("end", f"{idx}. {s['category']} - {s['service']} | Qty: {s['quantity']} {s['unit']} | Rate: ${s['average_price']:.2f} | Subtotal: ${s['estimated_cost']:.2f}")

    def remove_service(self):
        selected = self.services_listbox.curselection()
        if not selected:
            return
        idx = selected[0]
        del self.services_list[idx]
        self.update_services_listbox()
        self.update_total_label()

    def calculate_total(self):
        return sum(s['estimated_cost'] for s in self.services_list)

    def update_total_label(self):
        total = self.calculate_total()
        self.total_label.config(text=f"Total: ${total:,.2f}")

    def export_to_pdf(self):
        if not self.services_list:
            messagebox.showerror("No Services", "Add at least one service before exporting.")
            return
        import time
        from datetime import datetime
        invoice_number = f"INV-{int(time.time())}"
        current_date = datetime.now().strftime("%B %d, %Y")
        customer_name = self.client_name_var.get().strip()
        if customer_name:
            clean_name = "".join(c for c in customer_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')
            default_filename = f"{clean_name}_{invoice_number}.pdf"
        else:
            default_filename = f"Estimate_{invoice_number}.pdf"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_filename
        )
        if not file_path:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Precision Build Pros - Estimate", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, txt="619 Shun Pike, Cottontown, TN 37048", ln=True, align="C")
        pdf.cell(0, 6, txt="precisionbuildprosllc@gmail.com", ln=True, align="C")
        pdf.cell(0, 6, txt="615-587-0757", ln=True, align="C")
        pdf.set_xy(-60, 15)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, txt=f"Invoice #: {invoice_number}", ln=True, align="R")
        pdf.set_xy(10, 50)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, txt=f"Estimate Date: {current_date}", ln=True, align="L")
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Client Information:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, txt=f"Client: {self.client_name_var.get()}", ln=True)
        pdf.cell(0, 6, txt=f"Address: {self.client_address_var.get()}", ln=True)
        pdf.cell(0, 6, txt=f"Phone: {self.client_phone_var.get()}", ln=True)
        pdf.cell(0, 6, txt=f"Email: {self.client_email_var.get()}", ln=True)
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Services:", ln=True)
        pdf.set_font("Arial", size=10)
        for s in self.services_list:
            pdf.cell(0, 6, txt=f"- {s['category']} | {s['service']} | Qty: {s['quantity']} {s['unit']} | Rate: ${s['average_price']:.2f} | Subtotal: ${s['estimated_cost']:.2f}", ln=True)
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=f"Total Estimate: ${self.calculate_total():,.2f}", ln=True)
        pdf.ln(15)
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(0, 6, txt="Note: This estimate is valid for 30 days from the date issued.", ln=True, align="L")
        try:
            pdf.output(file_path)
            messagebox.showinfo("Exported", f"Estimate exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def save_estimate(self):
        if not self.services_list:
            messagebox.showerror("No Services", "Add at least one service before saving.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        data = {
            "client": {
                "name": self.client_name_var.get(),
                "address": self.client_address_var.get(),
                "phone": self.client_phone_var.get(),
                "email": self.client_email_var.get()
            },
            "services": self.services_list
        }
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", f"Estimate saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_estimate(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            client = data.get("client", {})
            self.client_name_var.set(client.get("name", ""))
            self.client_address_var.set(client.get("address", ""))
            self.client_phone_var.set(client.get("phone", ""))
            self.client_email_var.set(client.get("email", ""))
            self.services_list = data.get("services", [])
            self.update_services_listbox()
            self.update_total_label()
            self.result_label.config(text="Estimate loaded.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def clear_all(self):
        self.client_name_var.set("")
        self.client_address_var.set("")
        self.client_phone_var.set("")
        self.client_email_var.set("")
        self.category_var.set("")
        self.service_var.set("")
        self.quantity_var.set("")
        self.unit_var.set("sqft")
        self.services_list = []
        self.update_services_listbox()
        self.update_total_label()
        self.result_label.config(text="")

if __name__ == "__main__":
    app = tb.Window(themename="superhero")  # Dark, premium theme
    PriceEstimatorApp(app)
    app.mainloop()