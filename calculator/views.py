from django.shortcuts import render
from .subnet_calc import calculate, vlsm_allocate

def home(request): # Home view for subnet calculator
    context = {}
     
    if request.method == "POST": # Handle POST request
        ip_address = request.POST.get("ip_address", "").strip() # Get IP address input and strip whitespace
        cidr_input = request.POST.get("cidr", "").strip() # Get CIDR input and strip whitespace
        hosts_input = request.POST.get("hosts", "").strip() # Get hosts input and strip whitespace

        try: # Validate and process inputs
            cidr = int(cidr_input)

            if cidr < 0 or cidr > 32:
                raise ValueError("CIDR must be between 0 and 32.")

            if hosts_input: # If hosts input is provided, process it for VLSM allocation
                host_list = [int(x.strip()) for x in hosts_input.split(",")]

                vlsm_result = vlsm_allocate(ip_address, cidr, host_list)
                context["vlsm"] = vlsm_result


            result = calculate(ip_address, cidr) # Calculate subnet information based on IP address and CIDR
            context["result"] = result # Store the result in the context

            context["ip_address"] = ip_address # Store the IP address in the context
            context["cidr"] = cidr # Store the CIDR in the context
            context["hosts"] = hosts_input # Store the hosts input in the context

        except ValueError as e: # Handle value errors
            context["error"] = str(e)
        except Exception:
            context["error"] = "Invalid input. Check IP, CIDR, or hosts." # Handle any other exceptions and provide a generic error message

    return render(request, "calculator/home.html", context) # This part renders the home template with the context