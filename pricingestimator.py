import tkinter as tk
from tkinter import ttk
import json
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fpdf import FPDF

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
        self.root = root
        self.root.title("Precision Build Pros - Price Estimator")
        self.root.geometry("900x700")

        # Client info variables
        self.client_name_var = tk.StringVar()
        self.client_address_var = tk.StringVar()
        self.client_phone_var = tk.StringVar()
        self.client_email_var = tk.StringVar()

        self.category_var = tk.StringVar()
        self.service_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="sqft")

        self.services_list = []  # List of dicts: {category, service, quantity, unit, price}

        self.create_widgets()

    def create_widgets(self):
        # --- Client Info Frame ---
        client_frame = ttk.LabelFrame(self.root, text="Client Information")
        client_frame.grid(column=0, row=0, columnspan=3, padx=10, pady=10, sticky="ew")
        client_frame.columnconfigure(1, weight=1)

        ttk.Label(client_frame, text="Name:").grid(column=0, row=0, sticky="w", padx=5, pady=2)
        ttk.Entry(client_frame, textvariable=self.client_name_var, width=30).grid(column=1, row=0, sticky="ew", padx=5, pady=2)
        ttk.Label(client_frame, text="Address:").grid(column=0, row=1, sticky="w", padx=5, pady=2)
        ttk.Entry(client_frame, textvariable=self.client_address_var, width=30).grid(column=1, row=1, sticky="ew", padx=5, pady=2)
        ttk.Label(client_frame, text="Phone:").grid(column=2, row=0, sticky="w", padx=5, pady=2)
        ttk.Entry(client_frame, textvariable=self.client_phone_var, width=20).grid(column=3, row=0, sticky="ew", padx=5, pady=2)
        ttk.Label(client_frame, text="Email:").grid(column=2, row=1, sticky="w", padx=5, pady=2)
        ttk.Entry(client_frame, textvariable=self.client_email_var, width=20).grid(column=3, row=1, sticky="ew", padx=5, pady=2)

        # --- Service Entry Frame ---
        service_frame = ttk.LabelFrame(self.root, text="Add Service")
        service_frame.grid(column=0, row=1, columnspan=3, padx=10, pady=10, sticky="ew")
        service_frame.columnconfigure(1, weight=1)

        ttk.Label(service_frame, text="Category:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.category_cb = ttk.Combobox(service_frame, textvariable=self.category_var, values=list(pricing.keys()), state="readonly")
        self.category_cb.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.category_cb.bind("<<ComboboxSelected>>", self.update_services)

        ttk.Label(service_frame, text="Service:").grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.service_cb = ttk.Combobox(service_frame, textvariable=self.service_var, state="readonly")
        self.service_cb.grid(column=1, row=1, padx=5, pady=5, sticky="ew")

        ttk.Label(service_frame, text="Quantity:").grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(service_frame, textvariable=self.quantity_var)
        self.quantity_entry.grid(column=1, row=2, padx=5, pady=5, sticky="ew")

        ttk.Label(service_frame, text="Unit:").grid(column=2, row=2, padx=5, pady=5, sticky="w")
        self.unit_cb = ttk.Combobox(service_frame, textvariable=self.unit_var, values=["sqft", "LF"], state="readonly", width=6)
        self.unit_cb.grid(column=3, row=2, padx=5, pady=5, sticky="w")
        self.unit_cb.bind("<<ComboboxSelected>>", self.update_unit_label)

        self.add_service_btn = ttk.Button(service_frame, text="Add Service to Estimate", command=self.add_service)
        self.add_service_btn.grid(column=1, row=3, padx=5, pady=10, sticky="ew")

        # --- Services List Frame ---
        list_frame = ttk.LabelFrame(self.root, text="Services in Estimate")
        list_frame.grid(column=0, row=2, columnspan=3, padx=10, pady=10, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.services_listbox = tk.Listbox(list_frame, height=8, width=80)
        self.services_listbox.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)
        self.remove_service_btn = ttk.Button(list_frame, text="Remove Selected Service", command=self.remove_service)
        self.remove_service_btn.grid(column=0, row=1, sticky="ew", padx=5, pady=5)

        # --- Estimate Actions Frame ---
        actions_frame = ttk.Frame(self.root)
        actions_frame.grid(column=0, row=3, columnspan=3, padx=10, pady=10, sticky="ew")
        actions_frame.columnconfigure((0,1,2,3), weight=1)

        self.export_pdf_btn = ttk.Button(actions_frame, text="Export to PDF", command=self.export_to_pdf)
        self.export_pdf_btn.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
        self.save_json_btn = ttk.Button(actions_frame, text="Save Estimate", command=self.save_estimate)
        self.save_json_btn.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.load_json_btn = ttk.Button(actions_frame, text="Load Estimate", command=self.load_estimate)
        self.load_json_btn.grid(column=2, row=0, padx=5, pady=5, sticky="ew")
        self.clear_btn = ttk.Button(actions_frame, text="Clear All", command=self.clear_all)
        self.clear_btn.grid(column=3, row=0, padx=5, pady=5, sticky="ew")

        # --- Result Label ---
        self.result_label = ttk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(column=0, row=4, columnspan=3, padx=10, pady=20, sticky="ew")
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def update_services(self, event=None):
        selected_category = self.category_var.get()
        if selected_category in pricing:
            services = list(pricing[selected_category].keys())
            self.service_cb['values'] = services
            self.service_cb.set('')

    def update_unit_label(self, event=None):
        # Optionally update label or UI if needed
        pass

    def add_service(self):
        category = self.category_var.get()
        service = self.service_var.get()
        quantity = self.quantity_var.get()
        unit = self.unit_var.get()
        if not (category and service and quantity):
            messagebox.showerror("Input Error", "Please fill in all service fields.")
            return
        try:
            quantity = float(quantity)
            price_range = pricing[category][service]
            average_price = sum(price_range) / 2
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
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def update_services_listbox(self):
        self.services_listbox.delete(0, tk.END)
        for idx, s in enumerate(self.services_list, 1):
            self.services_listbox.insert(tk.END, f"{idx}. {s['category']} - {s['service']} | Qty: {s['quantity']} {s['unit']} | Rate: ${s['average_price']:.2f} | Subtotal: ${s['estimated_cost']:.2f}")

    def remove_service(self):
        selected = self.services_listbox.curselection()
        if not selected:
            return
        idx = selected[0]
        del self.services_list[idx]
        self.update_services_listbox()

    def calculate_total(self):
        return sum(s['estimated_cost'] for s in self.services_list)

    def export_to_pdf(self):
        if not self.services_list:
            messagebox.showerror("No Services", "Add at least one service before exporting.")
            return
        
        # Generate sequential invoice number (using timestamp for uniqueness)
        import time
        invoice_number = f"INV-{int(time.time())}"
        
        # Create default filename using customer name and invoice number
        customer_name = self.client_name_var.get().strip()
        if customer_name:
            # Clean customer name for filename (remove invalid characters)
            clean_name = "".join(c for c in customer_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')
            default_filename = f"{clean_name}_{invoice_number}.pdf"
        else:
            default_filename = f"Estimate_{invoice_number}.pdf"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialvalue=default_filename
        )
        if not file_path:
            return
        
        pdf = FPDF()
        pdf.add_page()
        
        # Business Header - Centered
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Precision Build Pros - Estimate", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, txt="619 Shun Pike, Cottontown, TN 37048", ln=True, align="C")
        pdf.cell(0, 6, txt="precisionbuildprosllc@gmail.com", ln=True, align="C")
        pdf.cell(0, 6, txt="615-587-0757", ln=True, align="C")
        
        # Invoice number - Top right
        pdf.set_xy(-60, 15)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, txt=f"Invoice #: {invoice_number}", ln=True, align="R")
        
        pdf.ln(10)
        
        # Client Information
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Client Information:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, txt=f"Client: {self.client_name_var.get()}", ln=True)
        pdf.cell(0, 6, txt=f"Address: {self.client_address_var.get()}", ln=True)
        pdf.cell(0, 6, txt=f"Phone: {self.client_phone_var.get()}", ln=True)
        pdf.cell(0, 6, txt=f"Email: {self.client_email_var.get()}", ln=True)
        pdf.ln(8)
        
        # Services
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Services:", ln=True)
        pdf.set_font("Arial", size=10)
        for s in self.services_list:
            pdf.cell(0, 6, txt=f"- {s['category']} | {s['service']} | Qty: {s['quantity']} {s['unit']} | Rate: ${s['average_price']:.2f} | Subtotal: ${s['estimated_cost']:.2f}", ln=True)
        pdf.ln(8)
        
        # Total
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=f"Total Estimate: ${self.calculate_total():,.2f}", ln=True)
        
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
        self.result_label.config(text="")

    # Optionally, keep the old single-service estimate for reference
    def calculate_price(self):
        category = self.category_var.get()
        service = self.service_var.get()
        quantity = self.quantity_var.get()
        try:
            quantity = float(quantity)
            price_range = pricing[category][service]
            average_price = sum(price_range) / 2
            estimated_cost = quantity * average_price
            self.result_label.config(
                text=f"Estimated Cost: ${estimated_cost:,.2f}\n(Average rate: ${average_price:.2f} per unit)"
            )
        except Exception as e:
            self.result_label.config(text="Error: Please check your inputs.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PriceEstimatorApp(root)
    root.mainloop()