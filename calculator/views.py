from django.shortcuts import render
from .subnet_calc import calculate

def home(request):
    context = {}

    if request.method == "POST":
        ip_address = request.POST.get("ip_address", "").strip()
        cidr_input = request.POST.get("cidr", "").strip()

        try:
            cidr = int(cidr_input)

            if cidr < 0 or cidr > 32:
                raise ValueError("CIDR must be between 0 and 32.")

            result = calculate(ip_address, cidr)

            context["result"] = result
            context["ip_address"] = ip_address
            context["cidr"] = cidr

        except ValueError as e:
            context["error"] = str(e)
        except Exception:
            context["error"] = "Invalid input. Please enter a valid IPv4 address and CIDR."

    return render(request, "calculator/home.html", context)

