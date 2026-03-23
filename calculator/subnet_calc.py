# =========================
# CONSTANT
# =========================
binary_weights = [128, 64, 32, 16, 8, 4, 2, 1]


# =========================
# IP → binary string (32 bits)
# =========================
def ip_to_binary(ip_address):
    octets = ip_address.split('.')
    binary_octets = [format(int(o), '08b') for o in octets]
    return ''.join(binary_octets)


# =========================
# binary → IP string
# =========================
def binary_to_ip(binary_str):
    octets = []
    start = 0
    end = 8

    for _ in range(4):
        octets.append(binary_str[start:end])
        start = end
        end += 8

    result = []
    for octet in octets:
        total = 0
        for i in range(8):
            if octet[i] == "1":
                total += binary_weights[i]
        result.append(str(total))

    return '.'.join(result)


# =========================
# Split network & host bits
# =========================
def split_bits(binary_ip, cidr):
    network_bits = binary_ip[:cidr]
    host_bits = 32 - cidr

    if host_bits == 0:
        host_bits_str = ''
    else:
        host_bits_str = binary_ip[-host_bits:]

    return network_bits, host_bits_str, host_bits


# =========================
# Calculate network binary
# =========================
def get_network_binary(binary_ip, cidr):
    network_bits, host_bits_str, host_bits = split_bits(binary_ip, cidr)

    if host_bits == 0:
        return binary_ip

    network_host_part = host_bits_str.replace('1', '0')
    return network_bits + network_host_part

# =========================
# Calculate subnet mask from CIDR
# =========================
def cidr_to_subnet_mask(cidr):
    network_part = '1' * cidr
    host_part = '0' * (32 - cidr)

    binary_mask = network_part + host_part

    return binary_to_ip(binary_mask)


# =========================
# Calculate broadcast binary
# =========================
def get_broadcast_binary(binary_ip, cidr):
    network_bits, host_bits_str, host_bits = split_bits(binary_ip, cidr)

    if host_bits == 0:
        return binary_ip

    broadcast_host_part = host_bits_str.replace('0', '1')
    return network_bits + broadcast_host_part


# =========================
# Calculate usable range
# =========================
def get_usable_range(network_binary, broadcast_binary, cidr):
    network_ip = binary_to_ip(network_binary)
    broadcast_ip = binary_to_ip(broadcast_binary)

    if cidr == 32:
        return network_ip, network_ip

    elif cidr == 31:
        return network_ip, broadcast_ip

    else:
        network_int = int(network_binary, 2)
        broadcast_int = int(broadcast_binary, 2)

        first_binary = format(network_int + 1, '032b')
        last_binary = format(broadcast_int - 1, '032b')

        return binary_to_ip(first_binary), binary_to_ip(last_binary)


# =========================
# MAIN CALCULATE FUNCTION
# =========================
def calculate(ip_address, cidr):
    binary_ip = ip_to_binary(ip_address)

    network_binary = get_network_binary(binary_ip, cidr)
    broadcast_binary = get_broadcast_binary(binary_ip, cidr)

    network_ip = binary_to_ip(network_binary)
    broadcast_ip = binary_to_ip(broadcast_binary)
    subnet_mask = cidr_to_subnet_mask(cidr)

    first_ip, last_ip = get_usable_range(network_binary, broadcast_binary, cidr)

    return {
        "network": network_ip,
        "broadcast": broadcast_ip,
        "first": first_ip,
        "last": last_ip,
        "subnet_mask": subnet_mask,
    }


# =========================
# Calculate usable hosts for CIDR
# =========================
def usable_hosts(cidr):
    return (2 ** (32 - cidr)) - 2


# =========================
# Adjust CIDR if not enough hosts
# =========================
def adjust_cidr(initial_cidr, host_list):
    cidr = initial_cidr
    total_required = sum(host_list)

    while usable_hosts(cidr) < total_required:
        cidr -= 1

    return cidr


# =========================
# Find CIDR for each subnet
# =========================
def find_subnet_cidr(host):
    for j in range(32):
        if (2 ** j) >= (host + 2):
            return 32 - j, (2 ** j) - 2


# =========================
# VLSM PLAN
# =========================
def vlsm_plan(initial_cidr, host_list):
    sorted_hosts = sorted(host_list, reverse=True)

    print("Initial usable hosts:", usable_hosts(initial_cidr))

    final_cidr = adjust_cidr(initial_cidr, sorted_hosts)

    print("Final CIDR:", final_cidr)
    print("Total usable:", usable_hosts(final_cidr))
    print("Total required:", sum(sorted_hosts))
    print("Sorted hosts:", sorted_hosts)

    print("\nSubnet allocation:")

    result = []

    for host in sorted_hosts:
        cidr, usable = find_subnet_cidr(host)

        print(f"Hosts: {host} -> /{cidr} (usable: {usable})")

        result.append({
            "hosts": host,
            "cidr": cidr,
            "usable": usable
        })

    return result


# =========================
# Add 1 to binary string
# =========================
def add_one_binary(binary_str):
    binary_list = list(binary_str)

    for i in range(len(binary_list) - 1, -1, -1):
        if binary_list[i] == '0':
            binary_list[i] = '1'
            break
        else:
            binary_list[i] = '0'

    return ''.join(binary_list)


# =========================
# FINAL VLSM ALLOCATION
# =========================
def vlsm_allocate(base_ip, base_cidr, host_list):
    plan = vlsm_plan(base_cidr, host_list)

    print("\n=========================")
    print("VLSM ALLOCATION RESULT")
    print("=========================")

    current_ip = base_ip
    result = []

    for subnet in plan:
        cidr = subnet["cidr"]

        subnet_info = calculate(current_ip, cidr)

        print(f"""
        Hosts: {subnet["hosts"]}
        Hosts Available: {subnet["usable"]}
        CIDR: /{cidr}
        Subnet Mask: {subnet_info["subnet_mask"]}
        Network: {subnet_info["network"]}
        Broadcast: {subnet_info["broadcast"]}
        Usable: {subnet_info["first"]} - {subnet_info["last"]}
        """)

        result.append({
            "hosts": subnet["hosts"],
            "hosts_available": subnet["usable"],
            "cidr": cidr,
            "subnet_mask": subnet_info["subnet_mask"],
            "network": subnet_info["network"],
            "broadcast": subnet_info["broadcast"],
            "first": subnet_info["first"],
            "last": subnet_info["last"],
        })

        # Move to next subnet (pure binary)
        broadcast_binary = ip_to_binary(subnet_info["broadcast"])
        next_binary = add_one_binary(broadcast_binary)
        current_ip = binary_to_ip(next_binary)

    return result