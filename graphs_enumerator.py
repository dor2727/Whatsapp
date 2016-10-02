#!/usr/bin/env py3
import whatsapp_parser as wp

print("[*] Message Statistics")
print("    [*] pie")
wp.utils.plot.pie(wp.d.user_message_amount, labels=wp.d.users, title="Message amount")
print("    [*] bar")
wp.utils.plot.bar(wp.d.user_message_amount, names=wp.d.users, title="Message amount")

print("[*] Media Statistics")
print("    [*] pie")
wp.utils.plot.pie(wp.d.user_media_amount, labels=wp.d.users, title="Media amount")
print("    [*] bar")
wp.utils.plot.bar(wp.d.user_media_amount, names=wp.d.users, title="Media amount")

print("[*] Absolue H amount")
print("    [*] pie")
wp.utils.plot.pie(wp.d.user_h_amount, labels=wp.d.users, title="Absolue H amount")
print("    [*] bar")
wp.utils.plot.bar(wp.d.user_h_amount, names=wp.d.users, title="Absolue H amount")

print("[*] H / message")
print("    [*] pie")
wp.utils.plot.pie(wp.d.user_hpm, labels=wp.d.users, title="H / message")
print("    [*] bar")
wp.utils.plot.bar(wp.d.user_hpm, names=wp.d.users, title="H / message")

print("[*] H / data")
print("    [*] pie")
wp.utils.plot.pie(list(map(lambda x:x*100, wp.d.user_hpd)), labels=wp.d.users, title="H / data")
print("    [*] bar")
wp.utils.plot.bar(wp.d.user_hpd, names=wp.d.users, title="H / data")

print("[*] Top 10 Emoji")
wp.d.plot_emojis(10)
print("[*] Top 5 Emoji by user")
wp.d.plot_emojis_by_users()

print("[*] Top 30 Words")
wp.d.get_most_common_words(30,1,1)

print("[*] Who's the funniest")
wp.whos_the_funniest(wp.d)

print("[*] First Message")
print("    " + str(wp.d.lines[0][0]))

print("[*] Most active...")
print("    [*] Hour")
wp.utils.plot.hours(wp.d.lines, delta=1)
print("    [*] Day")
wp.utils.plot.days(wp.d.lines)
print("    [*] Month")
wp.utils.plot.months(wp.d.lines)
