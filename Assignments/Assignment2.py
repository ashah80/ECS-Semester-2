import struct
import sys

def parse_elf_header(filename):
    """
    Parses the ELF header of a given ELF file and returns a dictionary of its fields.
    """
     
    with open(filename, "rb") as f:

        # ELF header is 64 bytes for 64-bit ELF files
        ELF_HEADER_SIZE = 64 
        header_data = f.read(ELF_HEADER_SIZE)

    # Unpack the ELF header using a format string
    # uint16_t: H, uint32_t: I, uint64_t: Q, char[16]: 16s (string of 16 bytes)
    fields = struct.unpack("16sHHIQQQIHHHHHH", header_data)

    # Figure out the endianness and then reparse
    if fields[0][5] == 1:  # Little-endian
        fields = struct.unpack("<16sHHIQQQIHHHHHH", header_data)
    elif fields[0][5] == 2:  # Big-endian
        fields = struct.unpack(">16sHHIQQQIHHHHHH", header_data)

    # Dictionary to hold the ELF header fields
    elf_header = {
        "e_ident": fields[0],
        "e_type (object file type)": fields[1],
        "e_machine (required architecture for an individual file)": fields[2],
        "e_version (object file version)": fields[3],
        "e_entry (the virtual address to which the system first transfers control)": fields[4],
        "e_phoff (the program header table's file offset)": fields[5],
        "e_shoff (the section header table's file offset)": fields[6],
        "e_flags (processor-specific flags associated with the file)": fields[7],
        "e_ehsize (the ELF header's size in bytes)": fields[8],
        "e_phentsize (the size in bytes of one entry in the file's program header table)": fields[9],
        "e_phnum (the number of entries in the program header table)": fields[10],
        "e_shentsize (a section header's size in bytes)": fields[11],
        "e_shnum (the number of entries in the section header table)": fields[12],
        "e_shstrndx (section header table index of the entry associated with the section name string table)": fields[13],
    }

    return elf_header

def parse_e_ident(e_ident):
    """
    Parses the e_ident field of the ELF header and returns a dictionary of its subfields.
    """

    # Dictionaries to map e_ident subfield values to human-readable strings
    EI_CLASS_DICT = {
        0: "Invalid class",
        1: "32-bit objects",
        2: "64-bit objects"
    }

    EI_DATA_DICT = {
        0: "Invalid data encoding",
        1: "Little-endian",
        2: "Big-endian"
    }

    EI_OSABI_DICT = {
            0: "No extensions or unspecified",
            1: "Hewlett-Packard HP-UX",
            2: "NetBSD",
            3: "Linux",
            6: "Sun Solaris",
            7: "AIX",
            8: "IRIX",
            9: "FreeBSD",
            10: "Compaq TRU64 UNIX",
            11: "Novell Modesto",
            12: "Open BSD",
            13: "Open VMS",
            14: "Hewlett-Packard Non-Stop Kernel"
    }

    # Dictionary to hold the e_ident subfields and their values for printing later
    e_ident_dict = {
        "EI_MAG ('magic number' identifying the file as an ELF object file)": f"0x7f: {e_ident[0]}, E: {e_ident[1]}, L: {e_ident[2]}, F: {e_ident[3]}",
        "EI_CLASS (file class or capacity)": EI_CLASS_DICT.get(e_ident[4], "Unknown"),
        "EI_DATA (data encoding)": EI_DATA_DICT.get(e_ident[5], "Unknown"),
        "EI_VERSION (file version)": e_ident[6],
        "EI_OSABI (operating system and ABI identification)": EI_OSABI_DICT.get(e_ident[7], "Architecture-specific value range"),
        "EI_ABIVERSION (ABI version)": e_ident[8],
        "EI_PAD (padding bytes)": list(e_ident[9:16])
    }

    return e_ident_dict

# Dictionaries to map ELF header field values to human-readable strings (except for e_ident which is more difficult to parse and gets its own function above)

E_TYPE_DICT = {
    0: "No file type",
    1: "Relocatable file",
    2: "Executable file",
    3: "Shared object file",
    4: "Core file"
}

E_MACHINE_DICT = {
    0: "No machine",
    1: "AT&T WE 32100",
    2: "SPARC",
    3: "Intel 80386",
    4: "Motorola 68000",
    5: "Motorola 88000",
    7: "Intel 80860",
    8: "MIPS I Architecture",
    9: "IBM System/370 Processor",
    10: "MIPS RS3000 Little-endian",
    15: "Hewlett-Packard PA-RISC",
    17: "Fujitsu VPP500",
    18: "Enhanced instruction set SPARC",
    19: "Intel 80960",
    20: "PowerPC",
    21: "64-bit PowerPC",
    22: "IBM System/390 Processor",
    36: "NEC V800",
    37: "Fujitsu FR20",
    38: "TRW RH-32",
    39: "Motorola RCE",
    40: "Advanced RISC Machines ARM",
    41: "Digital Alpha",
    42: "Hitachi SH",
    43: "SPARC Version 9",
    44: "Siemens TriCore embedded processor",
    45: "Argonaut RISC Core, Argonaut Technologies Inc.",
    46: "Hitachi H8/300",
    47: "Hitachi H8/300H",
    48: "Hitachi H8S",
    49: "Hitachi H8/500",
    50: "Intel IA-64 processor architecture",
    51: "Stanford MIPS-X",
    52: "Motorola ColdFire",
    53: "Motorola M68HC12",
    54: "Fujitsu MMA Multimedia Accelerator",
    55: "Siemens PCP",
    56: "Sony nCPU embedded RISC processor",
    57: "Denso NDR1 microprocessor",
    58: "Motorola Star*Core processor",
    59: "Toyota ME16 processor",
    60: "STMicroelectronics ST100 processor",
    61: "Advanced Logic Corp. TinyJ embedded processor family",
    62: "AMD x86-64 architecture",
    63: "Sony DSP Processor",
    64: "Digital Equipment Corp. PDP-10",
    65: "Digital Equipment Corp. PDP-11",
    66: "Siemens FX66 microcontroller",
    67: "STMicroelectronics ST9+ 8/16 bit microcontroller",
    68: "STMicroelectronics ST7 8-bit microcontroller",
    69: "Motorola MC68HC16 Microcontroller",
    70: "Motorola MC68HC11 Microcontroller",
    71: "Motorola MC68HC08 Microcontroller",
    72: "Motorola MC68HC05 Microcontroller",
    73: "Silicon Graphics SVx",
    74: "STMicroelectronics ST19 8-bit microcontroller",
    75: "Digital VAX",
    76: "Axis Communications 32-bit embedded processor",
    77: "Infineon Technologies 32-bit embedded processor",
    78: "Element 14 64-bit DSP Processor",
    79: "LSI Logic 16-bit DSP Processor",
    80: "Donald Knuth's educational 64-bit processor",
    81: "Harvard University machine-independent object files",
    82: "SiTera Prism",
    83: "Atmel AVR 8-bit microcontroller",
    84: "Fujitsu FR30",
    85: "Mitsubishi D10V",
    86: "Mitsubishi D30V",
    87: "NEC v850",
    88: "Mitsubishi M32R",
    89: "Matsushita MN10300",
    90: "Matsushita MN10200",
    91: "picoJava",
    92: "OpenRISC 32-bit embedded processor",
    93: "ARC Cores Tangent-A5",
    94: "Tensilica Xtensa Architecture",
    95: "Alphamosaic VideoCore processor",
    96: "Thompson Multimedia General Purpose Processor",
    97: "National Semiconductor 32000 series",
    98: "Tenor Network TPC processor",
    99: "Trebia SNP 1000 processor",
    100: "STMicroelectronics (www.st.com) ST200 microcontroller"
}

E_VERSION_DICT = {
    0: "Invalid version",
    1: "Current version"
}


# Read filename from command line argument
binary_file = ""
if len(sys.argv) == 2:
    binary_file = sys.argv[1]
else:
    print("Usage: Assignment2.py <elf_binary> (no file extension)", file=sys.stderr)
    sys.exit()

header = parse_elf_header(binary_file)


# Print the ELF header fields and their values to standard output
print("ELF Header Fields:", file=sys.stdout)
for key, value in header.items():

    # If the field is e_ident, parse its fields using the parse_e_ident function and print the key-value pairs of the resulting dictionary
    if key == "e_ident":
        ident_dict = parse_e_ident(value)
        print("e_ident subfields:", file=sys.stdout)
        for ei_ident_key, ei_ident_value in ident_dict.items():
            print(f"\t{ei_ident_key}: {ei_ident_value}", file=sys.stdout)

    # For all other fields, use the appropriate dictionary to convert the value to a string if necessary before printing
    if key == "e_type (object file type)":
        value = E_TYPE_DICT.get(value, "Unknown")
    elif key == "e_machine (required architecture for an individual file)":
        value = E_MACHINE_DICT.get(value, "Unknown")
    elif key == "e_version (object file version)":
        value = E_VERSION_DICT.get(value, "Unknown")
        
    if key != "e_ident":
        print(f"{key}: {value}", file=sys.stdout)