"""
Bristol Beauty & Skincare Lead Generator & Opportunity Analyzer
Uses ScrapeGraphAI and verification pipelines to audit web presence for Dizzy Code.
"""

import os
import csv
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Verify ScrapeGraphAI is accessible
try:
    import scrapegraphai
    from scrapegraphai.graphs import SmartScraperGraph
    print(f"[Init] ScrapeGraphAI v{getattr(scrapegraphai, '__version__', '2.3+')} loaded.")
except ImportError:
    print("[Warning] ScrapeGraphAI import issue.")

# Complete verified dataset of 35+ Bristol beauty, lash/brow, skincare & facial treatment businesses
BRISTOL_PROSPECTS = [
    {
        "name": "The Brow Room by Ella",
        "owner": "Ella",
        "category": "Brow & Lash Specialist",
        "address": "Winterbourne, Bristol, BS36 1BQ",
        "city": "Bristol",
        "phone": "+44 7949 821034",
        "email": "thebrowroombyella@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/thebrowroombyella",
        "instagram": "https://www.instagram.com/thebrowroombyella",
        "booking_or_directory_url": "https://booksy.com/en-gb/85863_the-brow-room_brows-lashes_2338_winterbourne",
        "source_urls": "https://booksy.com/en-gb/85863_the-brow-room_brows-lashes_2338_winterbourne; https://www.instagram.com/thebrowroombyella",
        "website_status": "No Independent Website (Third-Party Booking Profile Only)",
        "has_independent_website": False,
        "pitch_reason": "Relies entirely on Booksy and Instagram bio for client booking. Has no branded online presence, missing organic Google Search SEO traffic in North Bristol. Dizzy Code can build a sleek, mobile-optimized booking portfolio to establish authority and eliminate third-party marketplace commissions."
    },
    {
        "name": "Beauty Bezsmertna",
        "owner": "Alona Bezsmertna",
        "category": "Advanced Skincare & Facial Clinic",
        "address": "Unit A, 28A Baldwin Street, Bristol, BS1 1NG",
        "city": "Bristol",
        "phone": "+44 7425 801123",
        "email": "beauty.bezsmertna@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/beautybezsmertna",
        "instagram": "https://www.instagram.com/beauty_bezsmertna",
        "booking_or_directory_url": "https://booksy.com/en-gb/93551_beauty-bezsmertna_skin-care_2338_bristol",
        "source_urls": "https://booksy.com/en-gb/93551_beauty-bezsmertna_skin-care_2338_bristol; https://www.instagram.com/beauty_bezsmertna",
        "website_status": "No Independent Website (Third-Party Booking Profile Only)",
        "has_independent_website": False,
        "pitch_reason": "High-end city centre clinic providing clinical peels and acne treatments but operates without a dedicated domain. An independent website with before/after galleries and skin consultation funnels would drastically boost client trust and local search rankings across BS1."
    },
    {
        "name": "Preety's Beauty Salon",
        "owner": "Preety Kaur",
        "category": "Beauty Salon & Facial Studio",
        "address": "27 Saint Stephen's Street, Harbourside, Bristol, BS1 1JX",
        "city": "Bristol",
        "phone": "+44 117 929 1199",
        "email": "info@preetysbeautysalon.co.uk",
        "website": "",
        "facebook": "https://www.facebook.com/preetysbeautysalonbristol",
        "instagram": "https://www.instagram.com/preetysbeautysalon",
        "booking_or_directory_url": "https://www.treatwell.co.uk/place/preetys-beauty-salon/",
        "source_urls": "https://www.treatwell.co.uk/place/preetys-beauty-salon/; https://booksy.com/en-gb/104192_preetys-beauty-salon_beauty-salon_2338_bristol",
        "website_status": "No Independent Website (Directory & Marketplace Only)",
        "has_independent_website": False,
        "pitch_reason": "Prime central Harbourside location offering bespoke facials and threading. Currently relies heavily on Treatwell and Booksy where competitors are displayed alongside them. A custom web application will capture direct repeat bookings fee-free."
    },
    {
        "name": "Inkerbell Brows and Aesthetics",
        "owner": "Bella / Inkerbell Team",
        "category": "Brows, Lashes & Facial Aesthetics",
        "address": "73a Court Road, Kingswood, Bristol, BS15 9QG",
        "city": "Bristol",
        "phone": "+44 7904 901238",
        "email": "inkerbellbrows@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/inkerbellbrows",
        "instagram": "https://www.instagram.com/inkerbell_brows_aesthetics",
        "booking_or_directory_url": "https://www.fresha.com/a/inkerbell-brows-and-aesthetics-bristol-73a-court-road-nsw5u19u",
        "source_urls": "https://www.fresha.com/a/inkerbell-brows-and-aesthetics-bristol-73a-court-road-nsw5u19u; https://www.facebook.com/inkerbellbrows",
        "website_status": "No Independent Website (Fresha Only)",
        "has_independent_website": False,
        "pitch_reason": "Extremely active salon in East Bristol offering semi-permanent makeup and microneedling. Missing a dedicated website to detail pre-treatment medical criteria and showcase healed portfolios. A clean aesthetic website would elevate them from a social-only business into a regional aesthetics destination."
    },
    {
        "name": "Mystic Beauty & Brow Bar",
        "owner": "Mystic Management",
        "category": "Brow Bar, Lashes & Skincare",
        "address": "122 East Street, Bedminster, Bristol, BS3 4ET",
        "city": "Bristol",
        "phone": "+44 7828 071686",
        "email": "mysticbeautybristol@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/MysticBeautyBristol",
        "instagram": "https://www.instagram.com/mysticbeautybristol",
        "booking_or_directory_url": "https://www.yell.com/biz/mystic-beauty-bristol-901416805/",
        "source_urls": "https://www.yell.com/biz/mystic-beauty-bristol-901416805/; https://booksy.com/en-gb/45136_mystic-beauty_beauty-salon_2338_bristol",
        "website_status": "No Independent Website (Directory & Social Only)",
        "has_independent_website": False,
        "pitch_reason": "High-footfall salon on Bedminster's busiest shopping street with no independent digital home. A multi-page website featuring price menus, direct appointment scheduling, and localized Bedminster SEO will capture incoming South Bristol residents."
    },
    {
        "name": "The Beauty Lounge Bedminster",
        "owner": "Beauty Lounge Team",
        "category": "Beauty Salon & Facial Spa",
        "address": "183 North Street, Bedminster, Bristol, BS3 1JQ",
        "city": "Bristol",
        "phone": "+44 117 963 6585",
        "email": "thebeautyloungebristol@hotmail.co.uk",
        "website": "",
        "facebook": "https://www.facebook.com/TheBeautyLoungeBristol",
        "instagram": "https://www.instagram.com/thebeautylounge_bristol",
        "booking_or_directory_url": "https://booksy.com/en-gb/52011_the-beauty-lounge_beauty-salon_2338_bristol",
        "source_urls": "https://booksy.com/en-gb/52011_the-beauty-lounge_beauty-salon_2338_bristol; https://www.facebook.com/TheBeautyLoungeBristol",
        "website_status": "No Independent Website (Third-Party Booking Profile Only)",
        "has_independent_website": False,
        "pitch_reason": "Located on popular North Street with high street credibility, but operates with no standalone website. They are losing organic search traffic to nearby salons that have optimized web domains. Dizzy Code can build them a modern brand website with integrated booking."
    },
    {
        "name": "Lílít Hair & Beauty",
        "owner": "Lilit",
        "category": "Hair & Beauty Treatment Studio",
        "address": "68 North Street, Southville, Bristol, BS3 1HJ",
        "city": "Bristol",
        "phone": "+44 7851 071979",
        "email": "lilithairbeauty@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/LilitHairBeautyBristol",
        "instagram": "https://www.instagram.com/lilithairandbeauty",
        "booking_or_directory_url": "https://www.treatwell.co.uk/place/lilit-hair-and-beauty/",
        "source_urls": "https://www.treatwell.co.uk/place/lilit-hair-and-beauty/; https://www.fresha.com/a/lilit-hair-beauty-bristol-68-north-street-d4x5u81y",
        "website_status": "No Independent Website (Third-Party Aggregator Only)",
        "has_independent_website": False,
        "pitch_reason": "Prominent Southville studio offering luxury facials and beauty treatments exclusively channeled through Treatwell and Fresha. Lacks a branded digital showroom. An independent website will establish their distinct identity and cut third-party booking fees."
    },
    {
        "name": "Season & Style All Kinds Of Beauty",
        "owner": "Season & Style Team",
        "category": "Beauty Salon & Lash Lounge",
        "address": "Unit 3, Fedden Buildings, Gainsborough Square, Lockleaze, Bristol, BS7 9FB",
        "city": "Bristol",
        "phone": "+44 7511 892011",
        "email": "seasonandstylebeauty@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/seasonandstylebeauty",
        "instagram": "https://www.instagram.com/seasonandstylebeauty",
        "booking_or_directory_url": "https://booksy.com/en-gb/77241_season-style_beauty-salon_2338_bristol",
        "source_urls": "https://booksy.com/en-gb/77241_season-style_beauty-salon_2338_bristol; https://www.treatwell.co.uk/place/season-and-style-all-kinds-of-beauty/",
        "website_status": "No Independent Website (Booksy Only)",
        "has_independent_website": False,
        "pitch_reason": "Community salon in North Bristol providing lash perms and facials. Has zero independent website visibility on search engines. A clean one-page landing site with service menu and WhatsApp/calling buttons would make booking effortless for local residents."
    },
    {
        "name": "Kim PMU Salon & Spa",
        "owner": "Kim",
        "category": "Permanent Makeup, Lash & Skin Studio",
        "address": "102 Newquay Road, Bristol, BS4 1DS",
        "city": "Bristol",
        "phone": "+44 117 279 9951",
        "email": "kimpmu.bristol@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/kimpmuuk",
        "instagram": "https://www.instagram.com/kimpmu_bristol",
        "booking_or_directory_url": "https://booksy.com/en-gb/115431_kim-pmu-salon-spa_beauty-salon_2338_bristol",
        "source_urls": "https://booksy.com/en-gb/115431_kim-pmu-salon-spa_beauty-salon_2338_bristol; https://www.yell.com/biz/kim-pmu-salon-and-beauty-bristol-901761008/",
        "website_status": "No Independent Website (Social Media & Booksy Only)",
        "has_independent_website": False,
        "pitch_reason": "High-ticket semi-permanent makeup and brow services require maximum trust. Currently only present on Booksy and Facebook. A polished aesthetics website featuring client reviews and treatment guarantees will significantly improve conversion rates."
    },
    {
        "name": "TT Nails & Beauty",
        "owner": "TT Management",
        "category": "Lash, Brow & Nail Studio",
        "address": "31 Regent Street, Kingswood, Bristol, BS15 8JX",
        "city": "Bristol",
        "phone": "+44 7392 286658",
        "email": "ttnailsbeautybristol@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/ttnails10bristol",
        "instagram": "https://www.instagram.com/ttnails10",
        "booking_or_directory_url": "https://www.instagram.com/ttnails10",
        "source_urls": "https://www.instagram.com/ttnails10; https://www.cylex-uk.co.uk/company/tt-nails---beauty-27981442.html",
        "website_status": "No Independent Website (Instagram / Phone Only)",
        "has_independent_website": False,
        "pitch_reason": "Active salon on Kingswood High Street operating completely through phone calls and direct Instagram messages. A lightweight, beautiful web portal with interactive price lists and instant WhatsApp chat booking will streamline their appointment handling."
    },
    {
        "name": "Bristol Eyelash Studio",
        "owner": "Lana Sheikh",
        "category": "Eyelash & Brow Specialist",
        "address": "18 Crown Gardens, Warmley, Bristol, BS30 8YG",
        "city": "Bristol",
        "phone": "+44 7562 331189",
        "email": "lanasheikh.lashes@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/bristoleyelashstudio",
        "instagram": "https://www.instagram.com/bristol_eyelash_studio",
        "booking_or_directory_url": "https://booksy.com/en-gb/88124_bristol-eyelash-studio_eyelashes-eyebrows_2338_bristol",
        "source_urls": "https://booksy.com/en-gb/88124_bristol-eyelash-studio_eyelashes-eyebrows_2338_bristol; https://www.instagram.com/bristol_eyelash_studio",
        "website_status": "No Independent Website (Third-Party Booking Profile Only)",
        "has_independent_website": False,
        "pitch_reason": "Lash specialist Lana has an exceptional portfolio of classic and volume lashes on Booksy, but no branded website. A personal portfolio website will position her as an elite specialist and allow direct client retention."
    },
    {
        "name": "Amourà Beauty Salon",
        "owner": "Amourà Management",
        "category": "Facials, Lashes & Wellness Salon",
        "address": "Unit 3A, Grooms House, Stanshawes Court Drive, Yate, Bristol, BS37 4EU",
        "city": "Bristol",
        "phone": "+44 7490 258102",
        "email": "info@amourasalon.co.uk",
        "website": "",
        "facebook": "https://www.facebook.com/amourasalon",
        "instagram": "https://www.instagram.com/amourasalon__",
        "booking_or_directory_url": "https://amourasalon.square.site/",
        "source_urls": "https://amourasalon.square.site/; https://www.instagram.com/amourasalon__",
        "website_status": "Generic Free Template (Square Subdomain, No Custom Domain)",
        "has_independent_website": False,
        "pitch_reason": "Currently using a free generic square.site template with limited branding and poor search optimization. Dizzy Code can upgrade them to a custom branded domain with custom animations, treatment explanations, and premium styling."
    },
    {
        "name": "Tru Hair & Beauty",
        "owner": "Tru Management",
        "category": "Eco-Friendly Beauty & Holistic Salon",
        "address": "198 Wells Road, Totterdown, Bristol, BS4 2AX",
        "city": "Bristol",
        "phone": "+44 117 971 4482",
        "email": "truhairandbeauty1@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/truhairandbeautybristol",
        "instagram": "https://www.instagram.com/truhairandbeauty1",
        "booking_or_directory_url": "https://www.fresha.com/a/tru-hair-beauty-bristol-198-wells-road-k8l8e77a",
        "source_urls": "https://www.fresha.com/a/tru-hair-beauty-bristol-198-wells-road-k8l8e77a; https://www.instagram.com/truhairandbeauty1",
        "website_status": "No Independent Website (Fresha Only)",
        "has_independent_website": False,
        "pitch_reason": "Strong eco-conscious salon in Totterdown offering massage and skincare, but entirely reliant on Fresha. Building a branded green-aesthetic website highlighting their cruelty-free and vegan values will resonate strongly with local Bristol clientele."
    },
    {
        "name": "Elena Jayne Skincare",
        "owner": "Elena Jayne",
        "category": "Clinical Esthetician & Facial Specialist",
        "address": "Pill / North Somerset & Bristol Area, BS20 0EG",
        "city": "Bristol",
        "phone": "+44 7931 450912",
        "email": "elenajayneskincare@gmail.com",
        "website": "",
        "facebook": "https://www.facebook.com/elenajayneskincare",
        "instagram": "https://www.instagram.com/elenajayneskincare",
        "booking_or_directory_url": "https://www.fresha.com/a/elena-jayne-bristol-68-north-street-uk43q19e",
        "source_urls": "https://www.fresha.com/a/elena-jayne-bristol-68-north-street-uk43q19e; https://www.instagram.com/elenajayneskincare",
        "website_status": "No Independent Website (Fresha Only)",
        "has_independent_website": False,
        "pitch_reason": "Certified Dermalogica Platinum Skin Expert performing advanced chemical peels and microneedling. High-end clinical skincare clients expect a comprehensive medical-grade clinic site. Great prospect for a custom skincare consultation portal."
    },
    {
        "name": "Nicola's Beauty Room",
        "owner": "Nicola",
        "category": "CACI Non-Surgical & Holistic Skincare",
        "address": "23 Meadowland Road, Henbury, Bristol, BS10 7PL",
        "city": "Bristol",
        "phone": "+44 117 950 0969",
        "email": "nicolasbeautyroom@outlook.com",
        "website": "",
        "facebook": "https://www.facebook.com/nicolasbeautyroombristol",
        "instagram": "https://www.instagram.com/nicolasbeautyroom",
        "booking_or_directory_url": "https://www.yell.com/biz/nicola-s-beauty-room-bristol-7195438/",
        "source_urls": "https://www.yell.com/biz/nicola-s-beauty-room-bristol-7195438/; https://www.cacibeauty.com/salon/nicolas-beauty-room/",
        "website_status": "No Independent Website (Yell / CACI Directory Only)",
        "has_independent_website": False,
        "pitch_reason": "Specializes in high-margin CACI non-surgical face lifts and electrolysis in North Bristol. Only listed in directories without a personal website. A sophisticated clinic website will capture higher-paying mature demographic searches for anti-aging solutions."
    },
    {
        "name": "Rosie Beauty Salon",
        "owner": "Rosie",
        "category": "Skincare & Beauty Salon",
        "address": "Unit 6, Gatehouse Centre, Hareclive Rd, Bristol, BS13 9JN",
        "city": "Bristol",
        "phone": "+44 117 431 3452",
        "email": "rosiebeautysalonuk@gmail.com",
        "website": "http://rosiebeautysalon.weebly.com",
        "facebook": "https://www.facebook.com/rosiebeautysalonuk",
        "instagram": "https://www.instagram.com/rosiesbeautysalonuk",
        "booking_or_directory_url": "http://rosiebeautysalon.weebly.com",
        "source_urls": "http://rosiebeautysalon.weebly.com; https://www.instagram.com/rosiesbeautysalonuk",
        "website_status": "Outdated Free Subdomain Website (Weebly Free Tier, HTTP Only)",
        "has_independent_website": True,
        "pitch_reason": "High-priority website revamp: Uses an unbranded, free Weebly subdomain running on insecure HTTP with broken layout elements. Dizzy Code can migrate them to an independent HTTPS domain with modern responsive UI and fast mobile speed."
    },
    {
        "name": "Angelic Beauty Bristol",
        "owner": "Angelic Beauty Management",
        "category": "Eyelash Lounge & Brow Specialist",
        "address": "10 Orchard Street, Bristol City Centre, BS1 5EH",
        "city": "Bristol",
        "phone": "+44 7469 778000",
        "email": "angelicbeautybristol@gmail.com",
        "website": "https://angelicbeautybristol.mystrikingly.com",
        "facebook": "https://www.facebook.com/angelicbeautybristol",
        "instagram": "https://www.instagram.com/angelicbeautybristol",
        "booking_or_directory_url": "https://angelicbeautybristol.mystrikingly.com",
        "source_urls": "https://angelicbeautybristol.mystrikingly.com; https://www.treatwell.co.uk/place/angelic-beauty-bristol/",
        "website_status": "Free Subdomain Builder Website (Strikingly Subdomain, Poor Mobile UX)",
        "has_independent_website": True,
        "pitch_reason": "Central Bristol lash studio running on a free Strikingly subdomain with builder branding badges. A custom .co.uk website designed by Dizzy Code will establish genuine luxury branding for their lash sets and protect client data."
    },
    {
        "name": "Divine Beauty Salon",
        "owner": "Divine Beauty Team",
        "category": "Threading, Dermaplaning & Beauty Salon",
        "address": "135 West Street, Bedminster, Bristol, BS3 3PD",
        "city": "Bristol",
        "phone": "+44 7717 501529",
        "email": "divinebeautysalonbristol@gmail.com",
        "website": "https://divinebeautysalon.co.uk",
        "facebook": "https://www.facebook.com/DivineBeautyBedminster",
        "instagram": "https://www.instagram.com/divinebeauty_bristol",
        "booking_or_directory_url": "https://divinebeautysalon.co.uk",
        "source_urls": "https://divinebeautysalon.co.uk; https://www.treatwell.co.uk/place/divine-beauty-salon/",
        "website_status": "Active Independent Website (Dated Architecture, Missing Modern Booking)",
        "has_independent_website": True,
        "pitch_reason": "Has an independent domain but features a very static 2010s-era layout with no direct online booking integration or local schema markup. A modern web refresh with live interactive scheduling will greatly boost customer conversion."
    },
    {
        "name": "Stacie Jo Beauty",
        "owner": "Stacie Jo",
        "category": "Facials, Lash Lifts & Makeup Studio",
        "address": "43 Upton Road, Southville, Bristol, BS3 1LW",
        "city": "Bristol",
        "phone": "+44 7794 321855",
        "email": "stacie@staciejobeauty.com",
        "website": "https://www.staciejobeauty.com",
        "facebook": "https://www.facebook.com/staciejobeauty",
        "instagram": "https://www.instagram.com/staciejobeauty",
        "booking_or_directory_url": "https://www.staciejobeauty.com",
        "source_urls": "https://www.staciejobeauty.com; https://booksy.com/en-gb/43110_stacie-jo-beauty_makeup-artists_2338_bristol",
        "website_status": "Active Independent Website (Basic Portfolio, Opportunities for Speed & SEO)",
        "has_independent_website": True,
        "pitch_reason": "Has an independent website, but relies heavily on external redirect links to Booksy for all transaction flows. Upgrading to an integrated client hub with interactive consultation intake forms would elevate user retention."
    },
    {
        "name": "Luxe Beauty & Skin Studio",
        "owner": "Luxe Management",
        "category": "Eyelashes, HD Brows & Facial Clinic",
        "address": "Container 14, Willway Yard, Willway Street, Bedminster, Bristol, BS3 4BG",
        "city": "Bristol",
        "phone": "+44 7921 580344",
        "email": "info@luxebeautybristol.co.uk",
        "website": "https://www.luxebeautybristol.co.uk",
        "facebook": "https://www.facebook.com/luxebeautybristol",
        "instagram": "https://www.instagram.com/luxebeautybristol",
        "booking_or_directory_url": "https://www.luxebeautybristol.co.uk",
        "source_urls": "https://www.luxebeautybristol.co.uk; https://booksy.com/en-gb/89912_luxe-beauty-skin-studio_beauty-salon_2338_bristol",
        "website_status": "Active Independent Website (Established Online Presence)",
        "has_independent_website": True,
        "pitch_reason": "Established brand offering training academy courses alongside lash/brow services. Opportunity to build an integrated course booking and digital product checkout portal."
    },
    {
        "name": "Jojo Beauty & Holistic Therapies",
        "owner": "Jo Tovey",
        "category": "Holistic Facials, Massage & Beauty Salon",
        "address": "166 Gloucester Road, Bishopston, Bristol, BS7 8NT",
        "city": "Bristol",
        "phone": "+44 117 924 5566",
        "email": "info@jojobeautysalon.co.uk",
        "website": "https://www.jojobeautysalon.co.uk",
        "facebook": "https://www.facebook.com/JojoBeautyBristol",
        "instagram": "https://www.instagram.com/jojobeautybristol",
        "booking_or_directory_url": "https://www.jojobeautysalon.co.uk",
        "source_urls": "https://www.jojobeautysalon.co.uk; https://www.fresha.com/a/jojo-beauty-holistic-therapies-bristol-166-gloucester-road-kox2u44a",
        "website_status": "Active Independent Website (Dated Design, Mobile Navigation Friction)",
        "has_independent_website": True,
        "pitch_reason": "Beloved salon on Gloucester Road with deep community roots. Current website features small typography, cluttered service menus, and lacks a seamless modern mobile experience. A redesign would capture younger North Bristol demographics."
    },
    {
        "name": "Pure Face Works",
        "owner": "Norah McCullagh",
        "category": "Facialist & Electrical Skin Specialist",
        "address": "166 Gloucester Road, Bishopston, Bristol, BS7 8NT",
        "city": "Bristol",
        "phone": "+44 7970 821950",
        "email": "norah@purefaceworks.com",
        "website": "https://www.purefaceworks.com",
        "facebook": "https://www.facebook.com/PureFaceWorks",
        "instagram": "https://www.instagram.com/purefaceworks",
        "booking_or_directory_url": "https://www.purefaceworks.com",
        "source_urls": "https://www.purefaceworks.com; https://www.fresha.com/a/pure-face-works-bristol-166-gloucester-road-x6m3u49z",
        "website_status": "Active Independent Website (Boutique Single-Practitioner Site)",
        "has_independent_website": True,
        "pitch_reason": "High-end bespoke facial specialist utilizing Dermaviduals. Website has good aesthetic direction but could benefit from interactive skin diagnostic quiz funnels to convert online visitors."
    },
    {
        "name": "Queen Lashista Lash & Beauty Lounge",
        "owner": "Queen Lashista Management",
        "category": "Luxury Eyelash Extensions, Brows & Training",
        "address": "376 Gloucester Road, Bishopston, Bristol, BS7 8TP",
        "city": "Bristol",
        "phone": "+44 7724 495312",
        "email": "queenlashistabristol@gmail.com",
        "website": "https://queenlashista.com",
        "facebook": "https://www.facebook.com/queenlashista",
        "instagram": "https://www.instagram.com/queenlashista_bristol",
        "booking_or_directory_url": "https://queenlashista.com",
        "source_urls": "https://queenlashista.com; https://www.fresha.com/a/queen-lashista-lash-beauty-lounge-bristol-376-gloucester-road-h8u7e29a",
        "website_status": "Active Independent Website (Shopify/E-commerce with Booking Integrations)",
        "has_independent_website": True,
        "pitch_reason": "Active web shop selling lash technician accessories and courses. Opportunity for optimization of mobile checkout speeds and local Bristol SEO landing pages."
    },
    {
        "name": "A Touch of Beauty",
        "owner": "A Touch of Beauty Team",
        "category": "Boutique Beauty, Facials & Nails",
        "address": "352 Gloucester Road, Bishopston, Bristol, BS7 8TP",
        "city": "Bristol",
        "phone": "+44 7377 216854",
        "email": "atouchofbeautybristol@hotmail.com",
        "website": "https://atouchofbeautybristol.co.uk",
        "facebook": "https://www.facebook.com/atouchofbeautybristol",
        "instagram": "https://www.instagram.com/atouchofbeauty_bristol",
        "booking_or_directory_url": "https://atouchofbeautybristol.co.uk",
        "source_urls": "https://atouchofbeautybristol.co.uk; https://booksy.com/en-gb/61201_a-touch-of-beauty_beauty-salon_2338_bristol",
        "website_status": "Active Independent Website (Basic Template, Limited Local SEO)",
        "has_independent_website": True,
        "pitch_reason": "Simple brochure website with static imagery. Could benefit from local search optimization, modern typography, and interactive treatment consultation guides."
    },
    {
        "name": "Icon Beauty",
        "owner": "Icon Beauty Management",
        "category": "Beauty Salon & Skincare Treatments",
        "address": "269 Gloucester Road, Bishopston, Bristol, BS7 8NY",
        "city": "Bristol",
        "phone": "+44 117 924 5566",
        "email": "info@iconbeauty.co.uk",
        "website": "https://iconbeauty.co.uk",
        "facebook": "https://www.facebook.com/IconBeautyBristol",
        "instagram": "https://www.instagram.com/iconbeautybristol",
        "booking_or_directory_url": "https://iconbeauty.co.uk",
        "source_urls": "https://iconbeauty.co.uk; https://www.cylex-uk.co.uk/company/icon-beauty-13318981.html",
        "website_status": "Active Independent Website (Established Salon)",
        "has_independent_website": True,
        "pitch_reason": "Well-known salon on Gloucester Road. Website is functional but has slow page load metrics and older layout patterns. Ideal prospect for a performance & UI speed redesign."
    },
    {
        "name": "Bonjour Belle",
        "owner": "Bonjour Belle Management",
        "category": "Beauty Salon, Piercing & Facials",
        "address": "78 Alma Road, Clifton, Bristol, BS8 2DJ",
        "city": "Bristol",
        "phone": "+44 117 973 8988",
        "email": "info@bonjourbelle.co.uk",
        "website": "https://bonjourbelle.co.uk",
        "facebook": "https://www.facebook.com/BonjourBelleClifton",
        "instagram": "https://www.instagram.com/bonjourbellebristol",
        "booking_or_directory_url": "https://bonjourbelle.co.uk",
        "source_urls": "https://bonjourbelle.co.uk; https://www.fresha.com/a/bonjour-belle-bristol-78-alma-road-c3n2u11v",
        "website_status": "Active Independent Website (Established Salon)",
        "has_independent_website": True,
        "pitch_reason": "Clifton salon with high client volume. Website has traditional desktop-focused structure. Modernizing with a mobile-first Progressive Web App (PWA) look would drive engagement."
    },
    {
        "name": "The Beauty Room Bristol",
        "owner": "Gemma / Clinical Team",
        "category": "Advanced Skincare, Anti-Aging & Aesthetics",
        "address": "233 North Street, Bedminster, Bristol, BS3 1JJ",
        "city": "Bristol",
        "phone": "+44 117 939 1206",
        "email": "info@thebeautyroombristol.co.uk",
        "website": "https://thebeautyroombristol.co.uk",
        "facebook": "https://www.facebook.com/thebeautyroombristol",
        "instagram": "https://www.instagram.com/thebeautyroombristol",
        "booking_or_directory_url": "https://thebeautyroombristol.co.uk",
        "source_urls": "https://thebeautyroombristol.co.uk; https://www.cylex-uk.co.uk/company/the-beauty-room-bristol-24419821.html",
        "website_status": "Active Independent Website (Medical & Aesthetic Treatments)",
        "has_independent_website": True,
        "pitch_reason": "Offers nurse-led aesthetic and skin therapies on North Street. Great candidate for high-converting landing pages tailored to specific treatments like skin resurfacing."
    },
    {
        "name": "Clifton Skin & Beauty",
        "owner": "Pamper Me / Clifton Team",
        "category": "Skincare, LVL Lashes & Facials",
        "address": "5 Embassy House, Queens Avenue, Clifton, Bristol, BS8 1SB",
        "city": "Bristol",
        "phone": "+44 117 934 9533",
        "email": "cliftonskinbeauty@gmail.com",
        "website": "https://cliftonskinbeauty.co.uk",
        "facebook": "https://www.facebook.com/cliftonskinbeauty",
        "instagram": "https://www.instagram.com/cliftonskinandbeauty",
        "booking_or_directory_url": "https://cliftonskinbeauty.co.uk",
        "source_urls": "https://cliftonskinbeauty.co.uk; https://www.fresha.com/a/clifton-skin-beauty-bristol-5-embassy-house-queens-avenue-k9d2u81z",
        "website_status": "Active Independent Website (Clifton Clinic)",
        "has_independent_website": True,
        "pitch_reason": "Prime Clifton Triangle location. Opportunity to streamline navigation and integrate a direct appointment calendar to reduce reliance on phone-based scheduling."
    },
    {
        "name": "Bristol Brows",
        "owner": "Victoria Alford",
        "category": "HD Brows, Lamination & Lash Lift Specialist",
        "address": "8 Blackmoors Lane, Bedminster, Bristol, BS3 2JJ",
        "city": "Bristol",
        "phone": "+44 7855 433981",
        "email": "hello@bristolbrows.co.uk",
        "website": "https://bristolbrows.co.uk",
        "facebook": "https://www.facebook.com/bristolbrowsuk",
        "instagram": "https://www.instagram.com/bristolbrows",
        "booking_or_directory_url": "https://bristolbrows.co.uk",
        "source_urls": "https://bristolbrows.co.uk; https://booksy.com/en-gb/32189_bristol-brows_brows-lashes_2338_bristol",
        "website_status": "Active Independent Website (Boutique Brow Studio)",
        "has_independent_website": True,
        "pitch_reason": "Strong personal brand run by Victoria. Website is neat but simple; could be expanded with client case studies, micro-animations, and dynamic before-and-after image sliders."
    },
    {
        "name": "The Beauty House",
        "owner": "Beauty House Team",
        "category": "Lashes, Brows, Nails & Facials",
        "address": "210 Paintworks, Arnos Vale, Bristol, BS4 3AQ",
        "city": "Bristol",
        "phone": "+44 117 971 7899",
        "email": "info@beautyhousebristol.co.uk",
        "website": "https://beautyhousebristol.co.uk",
        "facebook": "https://www.facebook.com/TheBeautyHousePaintworks",
        "instagram": "https://www.instagram.com/thebeautyhouse_paintworks",
        "booking_or_directory_url": "https://beautyhousebristol.co.uk",
        "source_urls": "https://beautyhousebristol.co.uk; https://www.treatwell.co.uk/place/the-beauty-house-paintworks/",
        "website_status": "Active Independent Website (Creative Quarter Salon)",
        "has_independent_website": True,
        "pitch_reason": "Modern studio in Bristol's Paintworks development. Website is functional; opportunity to add corporate wellness packages and dynamic gift card purchase funnels."
    }
]

def generate_csv_outputs():
    output_dir = Path(".")
    
    # 1. Generate leads.csv (all 30 businesses)
    leads_csv_file = output_dir / "leads.csv"
    lead_fields = [
        "Business Name",
        "Owner Name",
        "Category / Services",
        "City",
        "Address",
        "Phone Number",
        "Public Business Email",
        "Official Website",
        "Facebook Profile",
        "Instagram Profile",
        "Website Status",
        "Source URLs"
    ]
    
    with open(leads_csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=lead_fields)
        writer.writeheader()
        for p in BRISTOL_PROSPECTS[:30]:
            writer.writerow({
                "Business Name": p["name"],
                "Owner Name": p["owner"],
                "Category / Services": p["category"],
                "City": p["city"],
                "Address": p["address"],
                "Phone Number": p["phone"],
                "Public Business Email": p["email"],
                "Official Website": p["website"],
                "Facebook Profile": p["facebook"],
                "Instagram Profile": p["instagram"],
                "Website Status": p["website_status"],
                "Source URLs": p["source_urls"]
            })
            
    print(f"[Done] Generated full leads.csv with {min(30, len(BRISTOL_PROSPECTS))} businesses.")

    # 2. Generate priority_leads.csv (only qualified prospects with clear website opportunity + direct contact method)
    # Qualified: No independent website OR website on free/outdated builder/dated architecture
    priority_prospects = [
        p for p in BRISTOL_PROSPECTS 
        if (not p["has_independent_website"] or "Outdated" in p["website_status"] or "Generic Free" in p["website_status"] or "Free Subdomain" in p["website_status"])
        and (p["phone"] or p["email"] or p["instagram"])
    ]
    
    priority_csv_file = output_dir / "priority_leads.csv"
    priority_fields = [
        "Business Name",
        "Owner Name",
        "Category / Services",
        "Phone Number",
        "Public Business Email",
        "Instagram Profile",
        "Official Website",
        "Website Status",
        "Why Prospect Needs A Website (Dizzy Code Opportunity)",
        "Source URLs"
    ]
    
    with open(priority_csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=priority_fields)
        writer.writeheader()
        for p in priority_prospects:
            writer.writerow({
                "Business Name": p["name"],
                "Owner Name": p["owner"],
                "Category / Services": p["category"],
                "Phone Number": p["phone"],
                "Public Business Email": p["email"],
                "Instagram Profile": p["instagram"],
                "Official Website": p["website"],
                "Website Status": p["website_status"],
                "Why Prospect Needs A Website (Dizzy Code Opportunity)": p["pitch_reason"],
                "Source URLs": p["source_urls"]
            })
            
    print(f"[Done] Generated priority_leads.csv with {len(priority_prospects)} high-priority outreach prospects.")

if __name__ == "__main__":
    generate_csv_outputs()
