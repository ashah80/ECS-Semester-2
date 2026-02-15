#include <stdio.h>
#include <stdint.h>
#define EI_NIDENT 16
typedef struct
{
    union
    {
        struct
        {
            uint8_t mag0;
            uint8_t mag1;
            uint8_t mag2;
            uint8_t mag3;
            uint8_t class;
            uint8_t data;
            uint8_t version;
            uint8_t osabi;
            uint8_t abiversion;
            uint8_t pad;
            uint8_t nident;
        } e_ident;
        unsigned char raw[EI_NIDENT];
    };
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint64_t e_entry;
    uint64_t e_phoff;
    uint64_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
} Elf64_Ehdr;
enum
{
    ET_NONE = 0,
    ET_REL,
    ET_EXEC,
    ET_DYN,
    ET_CORE,
};
enum
{
    EM_NONE = 0,
    EM_M32,
    EM_SPARC,
    EM_386,
    EM_68K,
    EM_88K,
    EM_860 = 7,
    EM_MIPS,
    EM_S370,
    EM_MIPS_RS3_LE,
    EM_PARISC = 15,
    EM_VPP500 = 17,
    EM_SPARC32PLUS,
    EM_960,
    EM_PPC,
    EM_PPC64,
    EM_S390,
    EM_V800 = 36,
    EM_FR20,
    EM_RH32,
    EM_RCE,
    EM_ARM,
    EM_ALPHA,
    EM_SH,
    EM_SPARCV9,
    EM_TRICORE,
    EM_ARC,
    EM_H8_300,
    EM_H8_300H,
    EM_H8S,
    EM_H8_500,
    EM_IA_64,
    EM_MIPS_X,
    EM_COLDFIRE,
    EM_68HC12,
    EM_MMA,
    EM_PCP,
    EM_NCPU,
    EM_NDR1,
    EM_STARCORE,
    EM_ME16,
    EM_ST100,
    EM_TINYJ,
    EM_X86_64,
    EM_PDSP,
    EM_PDP10,
    EM_PDP11,
    EM_FX66,
    EM_ST9PLUS,
    EM_ST7,
    EM_68HC16,
    EM_68HC11,
    EM_68HC08,
    EM_68HC05,
    EM_SVX,
    EM_ST19,
    EM_VAX,
    EM_CRIS,
    EM_JAVELIN,
    EM_FIREPATH,
    EM_ZSP,
    EM_MMIX,
    EM_HUANY,
    EM_PRISM,
    EM_AVR,
    EM_FR30,
    EM_D10V,
    EM_D30V,
    EM_V850,
    EM_M32R,
    EM_MN10300,
    EM_MN10200,
    EM_PJ,
    EM_OPENRISC,
    EM_ARC_A5,
    EM_XTENSA,
    EM_VIDEOCORE,
    EM_TMM_GPP,
    EM_NS32K,
    EM_TPC,
    EM_SNP1K,
    EM_ST200,
};
static char *machines[] = {
    [EM_NONE] = "No machine",
    [EM_M32] = "AT&T WE 32100",
    [EM_SPARC] = "SPARC",
    [EM_386] = "Intel 80386",
    [EM_68K] = "Motorola 68000",
    [EM_88K] = "Motorola 88000",
    [EM_860] = "Intel 80860",
    [EM_MIPS] = "MIPS I Architecture",
    [EM_S370] = "IBM System/370 Processor",
    [EM_MIPS_RS3_LE] = "MIPS RS3000 Little-endian",
    [EM_PARISC] = "Hewlett-Packard PA-RISC",
    [EM_VPP500] = "Fujitsu VPP500",
    [EM_SPARC32PLUS] = "Enhanced instruction set SPARC",
    [EM_960] = "Intel 80960",
    [EM_PPC] = "PowerPC",
    [EM_PPC64] = "64-bit PowerPC",
    [EM_S390] = "IBM System/390 Processor",
    [EM_V800] = "NEC V800",
    [EM_FR20] = "Fujitsu FR20",
    [EM_RH32] = "TRW RH-32",
    [EM_RCE] = "Motorola RCE",
    [EM_ARM] = "Advanced RISC Machines ARM",
    [EM_ALPHA] = "Digital Alpha",
    [EM_SH] = "Hitachi SH",
    [EM_SPARCV9] = "SPARC Version 9",
    [EM_TRICORE] = "Siemens TriCore embedded processor",
    [EM_ARC] = "Argonaut RISC Core, Argonaut Technologies Inc.",
    [EM_H8_300] = "Hitachi H8/300",
    [EM_H8_300H] = "Hitachi H8/300H",
    [EM_H8S] = "Hitachi H8S",
    [EM_H8_500] = "Hitachi H8/500",
    [EM_IA_64] = "Intel IA-64 processor architecture",
    [EM_MIPS_X] = "Stanford MIPS-X",
    [EM_COLDFIRE] = "Motorola ColdFire",
    [EM_68HC12] = "Motorola M68HC12",
    [EM_MMA] = "Fujitsu MMA Multimedia Accelerator",
    [EM_PCP] = "Siemens PCP",
    [EM_NCPU] = "Sony nCPU embedded RISC processor",
    [EM_NDR1] = "Denso NDR1 microprocessor",
    [EM_STARCORE] = "Motorola Star*Core processor",
    [EM_ME16] = "Toyota ME16 processor",
    [EM_ST100] = "STMicroelectronics ST100 processor",
    [EM_TINYJ] = "Advanced Logic Corp. TinyJ embedded processor family",
    [EM_X86_64] = "AMD x86-64 architecture",
    [EM_PDSP] = "Sony DSP Processor",
    [EM_PDP10] = "Digital Equipment Corp. PDP-10",
    [EM_PDP11] = "Digital Equipment Corp. PDP-11",
    [EM_FX66] = "Siemens FX66 microcontroller",
    [EM_ST9PLUS] = "STMicroelectronics ST9+ 8/16 bit microcontroller",
    [EM_ST7] = "STMicroelectronics ST7 8-bit microcontroller",
    [EM_68HC16] = "Motorola MC68HC16 Microcontroller",
    [EM_68HC11] = "Motorola MC68HC11 Microcontroller",
    [EM_68HC08] = "Motorola MC68HC08 Microcontroller",
    [EM_68HC05] = "Motorola MC68HC05 Microcontroller",
    [EM_SVX] = "Silicon Graphics SVx",
    [EM_ST19] = "STMicroelectronics ST19 8-bit microcontroller",
    [EM_VAX] = "Digital VAX",
    [EM_CRIS] = "Axis Communications 32-bit embedded processor",
    [EM_JAVELIN] = "Infineon Technologies 32-bit embedded processor",
    [EM_FIREPATH] = "Element 14 64-bit DSP Processor",
    [EM_ZSP] = "LSI Logic 16-bit DSP Processor",
    [EM_MMIX] = "Donald Knuth's educational 64-bit processor",
    [EM_HUANY] = "Harvard University machine-independent object files",
    [EM_PRISM] = "SiTera Prism",
    [EM_AVR] = "Atmel AVR 8-bit microcontroller",
    [EM_FR30] = "Fujitsu FR30",
    [EM_D10V] = "Mitsubishi D10V",
    [EM_D30V] = "Mitsubishi D30V",
    [EM_V850] = "NEC v850",
    [EM_M32R] = "Mitsubishi M32R",
    [EM_MN10300] = "Matsushita MN10300",
    [EM_MN10200] = "Matsushita MN10200",
    [EM_PJ] = "picoJava",
    [EM_OPENRISC] = "OpenRISC 32-bit embedded processor",
    [EM_ARC_A5] = "ARC Cores Tangent-A5",
    [EM_XTENSA] = "Tensilica Xtensa Architecture",
    [EM_VIDEOCORE] = "Alphamosaic VideoCore processor",
    [EM_TMM_GPP] = "Thompson Multimedia General Purpose Processor",
    [EM_NS32K] = "National Semiconductor 32000 series",
    [EM_TPC] = "Tenor Network TPC processor",
    [EM_SNP1K] = "Trebia SNP 1000 processor",
    [EM_ST200] = "STMicroelectronics (www.st.com) ST200 microcontroller",
};
void pr_type(Elf64_Ehdr *header)
{
    printf("Type: ");
    switch (header->e_type)
    {
    case ET_NONE:
        printf("None\n");
        break;
    case ET_REL:
        printf("Relocatable File\n");
        break;
    case ET_EXEC:
        printf("Executable\n");
        break;
    case ET_DYN:
        printf("Shared Object\n");
        break;
    case ET_CORE:
        printf("Core file\n");
        break;
    default:
        printf("Unknown\n");
    }
}
void pr_machine(Elf64_Ehdr *header)
{
    printf("Machine: %s\n", machines[header->e_machine]);
}
int main(void)
{
    Elf64_Ehdr header;
    FILE *fp;
    fp = fopen("wc", "r");
    fread(&header, sizeof(Elf64_Ehdr), 1, fp);
    pr_type(&header);
    pr_machine(&header);
    return 0;
}
