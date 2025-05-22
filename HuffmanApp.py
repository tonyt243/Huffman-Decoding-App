import os
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  
from collections import Counter

# Node Class for Building Huffman Tree Nodes
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

# Function to build Huffman Tree
def build_huffman_tree(text):
    if not text:
        return None, {}
    
    frequency = Counter(text)
    
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left 
        merged.right = right
        heapq.heappush(heap, merged)
    
    root = heap[0]
    huffman_codes = {}
    
    def generate_codes(node, current_code=""): 
        if node:
            if node.char is not None: # generates code by checking that node is not None
                huffman_codes[node.char] = current_code
            generate_codes(node.left, current_code + "0") 
            generate_codes(node.right, current_code + "1")
    
    generate_codes(root)
    return root, huffman_codes

def compress_text(text, progess_bar=None):
    root, huffman_codes = build_huffman_tree(text)
    compressed_text = ""
    total_chars = len(text)
    
    
    for idx, char in enumerate(text):
        compressed_text += huffman_codes[char]
        if progess_bar:
            progess_bar(idx + 1, total_chars)  
    
    return compressed_text, huffman_codes #return the compressed binary string and the Huffman codes


def decompress_text(compressed_text, huffman_codes, progess_bar=None):
    if not compressed_text or not huffman_codes: #if input is empty return an empty string
        return ""
    
    reverse_codes = {code: char for char, code in huffman_codes.items()} 
    decoded_text = "" #this holds the decompressed text
    temporary_code = "" 
    total_bits = len(compressed_text)
    
    for idx, bit in enumerate(compressed_text): #iterates over each bit in the text 
        temporary_code += bit
        if temporary_code in reverse_codes: # if temporary_code forms a huffman code then decode it
            decoded_text += reverse_codes[temporary_code]
            temporary_code = ""
        if progess_bar:
            progess_bar(idx + 1, total_bits)  
    
    return decoded_text

class HuffmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman Compression Tool")
        self.root.geometry("500x600")

        self.title_label = tk.Label(root, text=" Huffman Compression Tool ", font=("Times New Roman", 20, "bold"))
        self.title_label.pack(pady=10)

        self.select_file_btn = tk.Button(root, text="📂 Select File", command=self.select_file)
        self.select_file_btn.pack(pady=10)

        self.file_label = tk.Label(root, text="No file selected", wraplength=400)
        self.file_label.pack(pady=5)

        self.compress_btn = tk.Button(root, text=" Compress", command=self.compress_file, state=tk.DISABLED)
        self.compress_btn.pack(pady=10)

        self.decompress_btn = tk.Button(root, text=" Decompress", command=self.decompress_file, state=tk.DISABLED)
        self.decompress_btn.pack(pady=10)

        self.clear_btn = tk.Button(root, text="❌ Clear File", command=self.clear_interface)
        self.clear_btn.pack(pady=10)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack(pady=10)

        
        # Add progress bar
        style = ttk.Style()
        style.theme_use('xpnative')
        style.configure("TProgressbar", thickness=60)  

        self.progress = ttk.Progressbar(root, length=400, mode="determinate", style="TProgressbar")
        self.progress.pack(pady=10)


        self.huffman_frame = tk.Frame(root)
        self.huffman_frame.pack(pady=10)

        self.huffman_label = tk.Label(self.huffman_frame, text=" Generated Huffman Codes:", font=("Times New Roman", 12, "bold"))
        self.huffman_label.pack()

        huffman_scrollbar = tk.Scrollbar(self.huffman_frame)
        huffman_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.huffman_text = tk.Text(self.huffman_frame, height=8, width=50, wrap=tk.WORD, yscrollcommand=huffman_scrollbar.set)
        self.huffman_text.pack(pady=5)

        huffman_scrollbar.config(command=self.huffman_text.yview)
 

        self.decompressed_frame = tk.Frame(root)
        self.decompressed_frame.pack(pady=10)

        self.decompressed_label = tk.Label(self.decompressed_frame, text=" Decompressed Text:", font=("Times New Roman", 12, "bold"))
        self.decompressed_label.pack()

        decompressed_scrollbar = tk.Scrollbar(self.decompressed_frame)
        decompressed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.decompressed_text = tk.Text(self.decompressed_frame, height=8, width=50, wrap=tk.WORD, yscrollcommand=decompressed_scrollbar.set)
        self.decompressed_text.pack(pady=5)

        decompressed_scrollbar.config(command=self.decompressed_text.yview)
        
        self.compressed_text = ""
        self.huffman_codes = {}
        self.filepath = None 

    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.filepath:
            self.file_label.config(text=f"✅ Selected: {self.filepath}")
            self.compress_btn.config(state=tk.NORMAL)

    def update_progress(self, current, total):
        self.progress["value"] = (current / total) * 100
        self.root.update_idletasks()

    def compress_file(self):
        if self.filepath:
            self.status_label.config(text=" Compressing...", fg="green")
            with open(self.filepath, "r") as file:
                text = file.read()

            self.compressed_text, self.huffman_codes = compress_text(text, progess_bar=self.update_progress)
            self.huffman_text.config(state=tk.NORMAL)
            self.huffman_text.delete("1.0", tk.END)
            for char, code in self.huffman_codes.items():
                self.huffman_text.insert(tk.END, f"🔹 {char}: {code}\n")
            self.huffman_text.config(state=tk.DISABLED)

            messagebox.showinfo("Compression", " File compressed successfully!")
            self.decompress_btn.config(state=tk.NORMAL)

            original_size = os.path.getsize(self.filepath)
            compressed_size = len(self.compressed_text) // 8  

            messagebox.showinfo("Compression Stats",
                                f"Original Size: {original_size} bytes\nCompressed Size: {compressed_size} bytes\n"
                                f"Compression Ratio: {compressed_size/original_size:.2%}")

    def decompress_file(self):
        self.status_label.config(text="🔄 Decompressing...", fg="green")
        decompressed_text = decompress_text(self.compressed_text, self.huffman_codes, progess_bar=self.update_progress)

        self.decompressed_text.config(state=tk.NORMAL)
        self.decompressed_text.delete("1.0", tk.END)
        self.decompressed_text.insert(tk.END, f"{decompressed_text}\n")
        self.decompressed_text.config(state=tk.DISABLED)

        messagebox.showinfo("Decompression", " File decompressed successfully!")
    
    def clear_interface(self):
        self.filepath = None
        self.compressed_text = ""
        self.huffman_codes = {}

        self.file_label.config(text="No file selected")
        self.compress_btn.config(state=tk.DISABLED)
        self.decompress_btn.config(state=tk.DISABLED)
        self.status_label.config(text="")
        self.progress["value"] = 0

        self.huffman_text.config(state=tk.NORMAL)
        self.huffman_text.delete("1.0", tk.END)
        self.huffman_text.config(state=tk.DISABLED)

        self.decompressed_text.config(state=tk.NORMAL)
        self.decompressed_text.delete("1.0", tk.END)
        self.decompressed_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanGUI(root)
    root.mainloop()
