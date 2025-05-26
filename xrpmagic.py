import ctypes
import time
import argparse
import multiprocessing
from bip_utils import (
    Bip32Slip10Secp256k1,
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip39WordsNum,
    XrpAddrEncoder
)
from rich import print


def Main():
    # Setup argparse for command-line options
    parser = argparse.ArgumentParser(description="XRP Address Finder Script")
    
    parser.add_argument('-f', '--file', dest="filenameXrp", required=True,
                        help="XRP Rich Address File With Type Format .TXT [Example: -f xrp_rich.txt]")
    parser.add_argument('-v', '--view', dest="ViewPrint", required=True,
                        help="Print After Generating This Number of Addresses")
    parser.add_argument('-n', '--thread', dest="ThreadCount", required=True,
                        help="Total Number of Threads (Total Core CPU)")

    # Parse arguments
    args = parser.parse_args()
    filename = args.filenameXrp
    logpx = args.ViewPrint
    thco = args.ThreadCount

    # ----------------------- START ------------------------------ #
    with open(filename) as f:
        rich_addresses = f.read().split()
    rich_addresses = set(rich_addresses)

    generated_count = 0
    found_count = 0
    log_progress = 0

    while True:
        generated_count += 1
        ctypes.windll.kernel32.SetConsoleTitleW(f"MATCH:{found_count} SCAN:{generated_count}")
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_24)
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip32_mst_ctx = Bip32Slip10Secp256k1.FromSeed(seed_bytes)
        MasterKey = bip32_mst_ctx.PrivateKey().Raw().ToHex()
        bip32_der_ctx = bip32_mst_ctx.DerivePath("m/44'/144'/0'/0/0")
        PrivateKeyBytes = bip32_der_ctx.PrivateKey().Raw().ToHex()
        addr = XrpAddrEncoder.EncodeKey(bip32_der_ctx.PublicKey().KeyObject())
        Words24 = str(mnemonic)

        if addr in rich_addresses:
            found_count += 1
            print(f"[green1][+] MATCH ADDRESS FOUND IN LIST IMPORTED :[/green1] [white]{addr}[/white]")
            print(
                f"PrivateKey (Byte) : [green1]{PrivateKeyBytes}[/green1]\n[gold1]{mnemonic}[/gold1]\n[red1]MasterKey (Byte) : [/red1][green1]{MasterKey}[/green1]")
            with open('FoundMATCHAddr_XRP.txt', 'a') as f:
                f.write(
                    f"{addr}\n{PrivateKeyBytes}\n{mnemonic}\n{MasterKey}\n------------------------- MMDRZA.Com -------------------\n")
                f.close()
        elif int(generated_count) % int(logpx) == 0:
            log_progress += int(logpx)
            print(
                f"[red][[green1]+[/green1]][GENERATED[white] {log_progress}[/white] XRP ADDR][WITH [white]{thco} THREADS[/white]][sK/Th:[white]{time.thread_time()}[/white]][/red]\n[red][[green1]{PrivateKeyBytes.upper()}[/green1]][/red]")
            print(
                f"[red][MasterKey : [white]{MasterKey.upper()}[/white]][/red]\n[white on red3][MNEMONIC : {Words24[0:64]}...][/white on red3]")
        else:
            print(
                f"[red][-][ GENERATED [cyan]{generated_count}[/cyan] XRP ADDR ][FOUND:[white]{found_count}[/white]][THREAD:[cyan]{thco}[/cyan]][/red]",
                end="\r")


if __name__ == '__main__':
    jobs = []
    process = multiprocessing.Process(target=Main)
    jobs.append(process)
    process.start()
