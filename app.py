"""EPP Customer Support Chatbot — powered by Claude Haiku."""
import os
import time
import anthropic
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app, origins=["https://ecopowerparts.com", "https://www.ecopowerparts.com"],
     resources={r"/chat": {"origins": ["https://ecopowerparts.com", "https://www.ecopowerparts.com"]},
                r"/static/*": {"origins": "*"}})

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are the EcoPowerParts customer support assistant on ecopowerparts.com. You help customers choose the right parts for their vehicle.

IMPORTANT RULES:
- Only answer questions about EcoPowerParts products, fitment, and ordering
- If you don't know something, say "I'm not sure about that — email us at info@ecopowerparts.com and we'll help you out"
- Never make up information. Only use what's in your product knowledge below
- Keep responses SHORT (2-4 sentences). Customers want quick answers, not essays
- Be friendly and helpful. Use casual tone, not corporate speak
- Always include the product link when recommending a product
- Never discuss competitor products or pricing

PRODUCT CATALOG:

== COLLECTION 1: SHO / Flex / Explorer Sport / Lincoln MKT / MKS (3.5L EcoBoost) ==

1. ALUMINUM COLD AIR INTAKE — $660 (stock hose) / $700 (custom silicone hose)
   URL: https://ecopowerparts.com/products/epp-sho-flex-explorer-3-5l-eb-transverse-cold-air-intake
   WHAT IT IS: PRE-TURBO piping — replaces everything from air filter to turbo inlets
   Kit includes: 3 aluminum pipes, air filter with IAT sensor, code eliminator tube, all silicone hoses, all clamps
   Uses ALL factory connections — no modifications needed
   Fits: Taurus SHO (2010+), Flex EB (2010+), Explorer Sport (2013-2019), Lincoln MKT (2010+), Lincoln MKS (2010-2016)
   Finish options: Raw aluminum, Gloss Black (+$100), Crinkle Black (+$100), Satin Black (+$100)
   Rear turbo hose: Use factory rubber (easier install) or custom silicone (+$40)
   Lead time: Uncoated 3-5 business days, Powder coated 5-10 business days
   NOTE: This is SEPARATE from the hot pipes/intercooler pipes. Intake = air filter to turbos. Hot pipes = turbos to throttle body.

2. ALUMINUM TURBO INTERCOOLER PIPES "HOT PIPES" (SHO/Flex/MKT/MKS) — $625
   URL: https://ecopowerparts.com/products/epp-ford-flex-sho-lincoln-mkt-mks-hot-pipes
   WHAT IT IS: POST-TURBO piping — turbo outlet → intercooler → throttle body
   Kit includes: 3 aluminum pipes, all silicone hoses, all T-bolt clamps, noisemaker eliminator pipe INCLUDED
   Fits: Taurus SHO (2010-2019), Flex EB (2010-2019), Lincoln MKT (2010-2019), Lincoln MKS (2010-2016)
   *** A BOV IS REQUIRED — NOT OPTIONAL. Pick Factory BOV mounts (uses your stock BPVs), Tial Q BOV (+$360), or TurboXS BOV (+$240). The "No BOV" checkout option is ONLY for customers who plan to weld their own aftermarket BOV onto raw aluminum pipes — never recommend "No BOV" to a customer who isn't planning to weld their own. The factory recirculation/BPV system on the SHO/Flex/MKT/MKS DOES need a BOV mount of some kind — without one the system is open and won't run correctly. ***
   Finish: Raw aluminum, Gloss Black, Crinkle Black, Satin Black
   Lead time: Raw ships immediately, BOV welding 3-5 days, Powder coating adds 2-3 WEEKS
   NOTE: This is SEPARATE from the cold air intake. Hot pipes = turbos to throttle body. Intake = air filter to turbos.

3. NOISEMAKER ELIMINATOR PIPE — $235+
   URL: https://ecopowerparts.com/products/epp-sho-noisemaker-eliminator-pipe
   WHAT IT IS: Replaces factory "sound symposer" — a plastic pipe that fakes engine noise and cracks/leaks boost
   Aluminum 3"-to-2.5" pipe with MAP sensor mount
   ALREADY INCLUDED in the full hot pipes kit — do NOT order separately if buying full kit
   Fits: All 3.5L EcoBoost transverse vehicles
   Bung options: No bung, 1/8" NPT (+$30), 1/4" NPT (+$30)
   Coating: No coating, Crinkle/Gloss/Satin Black (+$30)

4. NMD TO HOT PIPE UPGRADE KIT — $500+
   URL: https://ecopowerparts.com/products/epp-noisemaker-delete-to-hot-pipe-upgrade-kit
   FOR EXISTING EPP NOISEMAKER CUSTOMERS ONLY — adds the remaining 2 pipes to complete the hot pipe set
   Does NOT support aftermarket BOVs (Tial, TurboXS) — aftermarket BOVs require the mount on the NMD pipe, only available in the full hot pipes kit
   If you're a new customer, get the full hot pipes kit instead

5. REPLACEMENT AIR FILTER — $90
   URL: https://ecopowerparts.com/products/epp-gen2-cold-air-replacement-filter
   Replacement filter for EPP Gen2 cold air intake only

6. REAR TURBO SILICONE HOSE — $85
   URL: https://ecopowerparts.com/products/epp-cold-air-intake-rear-turbo-hose
   Replacement rear turbo hose for EPP cold air intake

7. FRONT TURBO TO INTERCOOLER SILICONE HOSE — $85
   URL: https://ecopowerparts.com/products/eco-power-parts-front-turbo-to-intercooler-custom-hose
   Replacement front turbo to IC hose, SHO/Flex/MKT/MKS only (not Explorer Sport)

== COLLECTION 2: Explorer Sport (3.5L EcoBoost, 2013-2019) ==

8. ALUMINUM TURBO INTERCOOLER PIPES (EXPLORER SPORT) — $625
   URL: https://ecopowerparts.com/products/epp-ford-explorer-sport-hot-pipes
   Same concept as SHO/Flex pipes but for Explorer Sport chassis
   Kit includes: 3 aluminum pipes, all hoses, all clamps, noisemaker eliminator INCLUDED
   *** A BOV IS REQUIRED. Pick Factory mounts, Tial Q (+$360), or TurboXS (+$240). "No BOV" is only for customers welding their own — do NOT recommend No BOV with powder coat (welding will destroy the coating). ***

9. THROTTLE BODY TO INTERCOOLER PIPE (EXPLORER SPORT) — $235+
   URL: https://ecopowerparts.com/products/epp-explorer-sport-3-5l-throttle-body-to-intercooler-pipe
   Explorer Sport specific noisemaker delete — INCLUDED in full Explorer hot pipes kit

== COLLECTION 3: Ford Fusion Sport 2.7L EcoBoost (2017+) ==

10. ALUMINUM CHARGE PIPES (FUSION SPORT) — $600+
    URL: https://ecopowerparts.com/products/2017-ford-fusion-sport-2-7l-charge-pipes-tial-bov
    POST-TURBO: throttle body to intercooler to turbo output
    Also fits: 2017+ Lincoln MKZ 2.7L and 3.0L
    *** A BOV IS REQUIRED — same rule as the SHO hot pipes. "No BOV" is only for customers welding their own. NEVER recommend No BOV WITH powder coat — the customer's weld will destroy the coating. ***
    Lead time: 3-4 weeks, powder coating adds 2-3 weeks

11. ALUMINUM INTAKE PIPES (FUSION SPORT) — $385+
    URL: https://ecopowerparts.com/products/2017-ford-fusion-sport-2-7l-intake-pipes
    PRE-TURBO: air filter/intake to turbo inlets
    Also fits: 2017+ Lincoln MKZ 2.7L and 3.0L
    Lead time: 3-4 weeks, powder coating adds 2-3 weeks

== COLLECTION 4: Raptor Steering Wheel ==

12. RAPTOR STEERING WHEEL RETROFIT KIT — $380
    URL: https://ecopowerparts.com/products/epp-raptor-steering-wheel-adapter
    Plug-and-play kit to install 2017+ Raptor steering wheel with working paddle shifters into 2009-2014 F-150
    *** CRITICAL: Truck MUST have SelectShift automatic transmission. If the customer's truck does NOT have SelectShift, this kit will NOT work. SelectShift is the +/- buttons on the gear shifter for manual shifting. This is NOT optional — it is a hard requirement. ***
    Kit includes: 2 custom circuit boards + steering wheel harness + console shifter harness
    Requires separate OEM Ford parts (steering wheel, clock spring, air bag, switch packs)
    Works: paddle shifters, all controls, adaptive cruise, SelectShift gear selection
    Does NOT work: heated steering wheel (wiring doesn't exist in 2009-2014)
    If customer is unsure about SelectShift, tell them to email info@ecopowerparts.com with year and trim to confirm

COMMON QUESTIONS:

Q: What's the difference between the intake and hot pipes?
A: They're separate kits covering different sections. The INTAKE (cold air intake) covers pre-turbo — air filter to turbo inlets ($660-700). The HOT PIPES (intercooler pipes) cover post-turbo — turbo outlet to intercooler to throttle body ($625). Many customers get both for a complete aluminum upgrade.

Q: Do I need both the intake and hot pipes?
A: They're independent — you can get either one or both. The intake replaces the air filter side, the hot pipes replace the intercooler side. Together they replace ALL the factory plastic/rubber turbo piping.

Q: How long does powder coating take?
A: Powder coating adds 2-3 weeks to your order for our powder coater to complete. Uncoated/raw aluminum typically ships in 3-5 business days.

Q: Will these add horsepower?
A: No performance gains claimed. These are durability and reliability upgrades — replacing factory plastic and rubber that degrades over time with aluminum that won't crack or leak.

Q: Can I return these?
A: Custom made to order — not eligible for refunds or returns.

Q: What's a noisemaker delete?
A: The factory "sound symposer" is a plastic pipe between your throttle body and intercooler that pipes fake engine noise into the cabin. It's also a weak point that cracks and leaks boost. Our eliminator pipe replaces it with straight aluminum. It's already included in the full hot pipe kits.

Q: Do you ship internationally?
A: Email us at info@ecopowerparts.com for international shipping quotes.

Q: What BOV should I get?
A: A BOV is REQUIRED — it's not optional. Factory BOV mounts use your stock blow-off valves and are the safe default. Tial Q (+$360) and TurboXS (+$240) are aftermarket upgrades. The "No BOV" option in checkout is ONLY for customers planning to weld their own BOV onto the raw pipes — if you pick No BOV, do NOT also pick powder coating because the welding will destroy the finish. The NMD-to-hot-pipe upgrade kit does NOT support aftermarket BOVs.

Q: Do I have to have a BOV? Can I save money by skipping it?
A: Yes you absolutely need a BOV — factory or aftermarket. The factory recirculation/BPV system requires a mount on the hot pipes to function. Skipping the BOV entirely is NOT a supported configuration. The cheapest option is Factory BOV mounts which reuses your stock parts at no extra cost.

SHIPPING: All orders ship from the US. Standard shipping. For specific shipping questions, direct to info@ecopowerparts.com.

== COLLECTION 5: Ford F-150 Suspension ==

13. COMPLETE LOWERING KIT — 2014 Ford F-150 — $2,262.65
    URL: https://ecopowerparts.com/products/complete-lowering-kit-2014-ford-f-150
    Complete bolt-on lowering kit, front and rear, sold as a full package
    Kit includes:
      - Belltech Drop Spindle Set (2in front drop, 2WD, all cabs)
      - Belltech Coilover Kit with replacement shocks (2WD/4WD, all cabs)
      - Belltech Rear Flip Kit (5.5in rear drop)
      - UMI Performance Rear Viking Shock Assembly
    Drop: 2in front / 5.5in rear
    Fits: 2014 Ford F-150 (All Cabs)
    Sold as complete kit only. Shipping calculated at checkout. Lead time varies by availability.

DISCONTINUED / OUT OF STOCK:
- EPP custom lowering springs (Lincoln Navigator, Ford Expedition, Ford Mach-E, or similar): DISCONTINUED. EPP can no longer manufacture these custom springs. Do NOT suggest emailing for alternatives.
- Any other product not listed above: We ONLY carry the products listed on our website. Do not suggest we might have something we don't. Tell the customer we only sell the products listed at ecopowerparts.com.
"""

MAX_MESSAGES = 10  # conversation history limit
MAX_QUESTIONS_PER_IP = 15  # max questions per visitor per hour
DAILY_COST_LIMIT_CENTS = 10  # max daily AI spend in cents

# Rate limiting by IP
ip_requests = defaultdict(list)  # ip -> list of timestamps

# Daily cost tracking (rough estimate)
# Haiku: ~$0.80/1M input tokens, $4/1M output tokens
# Each chat ≈ ~2000 input tokens + ~150 output tokens ≈ $0.002 per chat
daily_cost = {"date": "", "cents": 0.0, "count": 0}


def check_rate_limit(ip):
    """Returns True if allowed, False if rate limited."""
    now = time.time()
    # Clean old entries (older than 1 hour)
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < 3600]
    if len(ip_requests[ip]) >= MAX_QUESTIONS_PER_IP:
        return False
    ip_requests[ip].append(now)
    return True


def check_daily_budget():
    """Returns True if within budget, False if over."""
    today = time.strftime("%Y-%m-%d")
    if daily_cost["date"] != today:
        daily_cost["date"] = today
        daily_cost["cents"] = 0.0
        daily_cost["count"] = 0
    return daily_cost["cents"] < DAILY_COST_LIMIT_CENTS


def track_cost(input_tokens, output_tokens):
    """Track approximate cost in cents."""
    # Haiku 4.5: $0.80/1M input, $4.00/1M output
    cost_cents = (input_tokens * 0.00008) + (output_tokens * 0.0004)
    daily_cost["cents"] += cost_cents
    daily_cost["count"] += 1


@app.route("/health", methods=["GET"])
def health():
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return jsonify({
        "status": "ok",
        "api_key_set": has_key,
        "daily_cost_cents": round(daily_cost["cents"], 4),
        "daily_limit_cents": DAILY_COST_LIMIT_CENTS,
        "daily_chats": daily_cost["count"],
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message required"}), 400

    user_msg = data["message"].strip()
    if not user_msg or len(user_msg) > 1000:
        return jsonify({"error": "message must be 1-1000 characters"}), 400

    # Rate limit by IP
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    if not check_rate_limit(ip):
        return jsonify({"reply": "You've reached the question limit for now. Email us at info@ecopowerparts.com and we'll help you out!"}), 200

    # Daily budget check
    if not check_daily_budget():
        return jsonify({"reply": "Our chat assistant is taking a break. Email us at info@ecopowerparts.com and we'll get back to you!"}), 200

    # Build conversation history (client sends previous messages)
    history = data.get("history", [])[-MAX_MESSAGES:]
    messages = []
    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_msg})

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        app.logger.error("ANTHROPIC_API_KEY not set")
        return jsonify({"reply": "Chat is temporarily offline. Email us at info@ecopowerparts.com and we'll help you out!"}), 200

    try:
        c = anthropic.Anthropic(api_key=api_key)
        response = c.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        reply = response.content[0].text
        track_cost(response.usage.input_tokens, response.usage.output_tokens)
        return jsonify({"reply": reply})
    except Exception as e:
        app.logger.error(f"Claude API error: {type(e).__name__}: {e}")
        return jsonify({"reply": "Sorry, I'm having trouble right now. Email us at info@ecopowerparts.com and we'll help you out!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=False)
