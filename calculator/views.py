from django.shortcuts import render
from .subnet_calc import calculate, vlsm_allocate

def home(request):
    context = {}

    if request.method == "POST":
        ip_address = request.POST.get("ip_address", "").strip()
        cidr_input = request.POST.get("cidr", "").strip()
        hosts_input = request.POST.get("hosts", "").strip()

        try:
            cidr = int(cidr_input)

            if cidr < 0 or cidr > 32:
                raise ValueError("CIDR must be between 0 and 32.")

            if hosts_input:
                host_list = [int(x.strip()) for x in hosts_input.split(",")]

                vlsm_result = vlsm_allocate(ip_address, cidr, host_list)
                context["vlsm"] = vlsm_result


            result = calculate(ip_address, cidr)
            context["result"] = result

            context["ip_address"] = ip_address
            context["cidr"] = cidr
            context["hosts"] = hosts_input

        except ValueError as e:
            context["error"] = str(e)
        except Exception:
            context["error"] = "Invalid input. Check IP, CIDR, or hosts."

    return render(request, "calculator/home.html", context)