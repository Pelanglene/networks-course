import logging
import subprocess
import argparse
import time
import icmplib
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def valid_mtu(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 100000000:
        raise argparse.ArgumentTypeError("MTU must be between 1 and 100000000")
    return ivalue


def is_address_reachable(destination):
    logging.info(f"Checking if address {destination} is reachable")
    result = icmplib.ping(destination)
    return result.is_alive


def find_mtu(destination, min_mtu, max_mtu, interval):
    low, high = min_mtu, max_mtu
    while low <= high:
        mid = (low + high) // 2

        data_size = mid - 28

        try:
            ping_res = icmplib.ping(
                destination,
                interval=interval,
                payload_size=data_size,
            )
        except icmplib.exceptions.NameLookupError:
            logging.error(f"Host {destination} cannot be resolved")
            exit(0)
        except icmplib.exceptions.DestinationUnreachable:
            logging.error(f'Host {destination} is unreachable')
            exit(0)
        except:
            logging.error('Unknown icmplib.ping error')
            exit(1)

        logging.info(f"Testing MTU size {mid} (ping size {data_size})")
        if ping_res.is_alive:
            low = mid + 1
        else:
            high = mid - 1
        time.sleep(interval)
    return high


if __name__ == '__main__':
    setup_logging()
    parser = argparse.ArgumentParser(description='MTU discovery script')
    parser.add_argument('--min_mtu', type=valid_mtu, required=True, help='Minimum MTU value to test')
    parser.add_argument('--max_mtu', type=valid_mtu, required=True, help='Maximum MTU value to test')
    parser.add_argument('--address', type=str, required=True, help='Destination address to test')
    parser.add_argument('--interval', type=float, default=0, help='Interval between attempts (seconds)')
    args = parser.parse_args()

    if not is_address_reachable(args.address):
        print("Address is not reachable")
        sys.exit(1)

    try:
        mtu = find_mtu(args.address, args.min_mtu, args.max_mtu, args.interval)
        if mtu:
            logging.info(f"The minimum MTU is: {mtu}")
        else:
            logging.error("Could not determine the MTU within the specified range.")
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        sys.exit(1)
