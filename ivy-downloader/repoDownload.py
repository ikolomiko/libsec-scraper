#!/usr/bin/env python3

lines = []
with open("repo_stats.csv", 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open("ivy-public.xml", 'w', encoding='utf-8') as f:
    header = """<ivysettings>
    <resolvers>
"""
    f.write(header)

    addition = """
        <ibiblio name="google-android-aar" m2compatible="true" root="https://dl.google.com/dl/android/maven2/" pattern="[organization]/[module]/[revision]/[module]-[revision].aar"/>
        <ibiblio name="google-android-jar" m2compatible="true" root="https://dl.google.com/dl/android/maven2/" pattern="[organization]/[module]/[revision]/[module]-[revision].[ext]" />
        <ibiblio name="mavenorg-aar" m2compatible="true" root="https://repo1.maven.org/maven2/" pattern="[organization]/[module]/[revision]/[module]-[revision].aar" />
        <ibiblio name="mavenorg-jar" m2compatible="true" />
"""
    f.write(addition)

    for line in lines:
        (name, usages, url) = line.strip().split(',')
        data = f"""
        <ibiblio name="{name}-aar" m2compatible="true" root="{url}" pattern="[organization]/[module]/[revision]/[module]-[revision].aar" />
        <ibiblio name="{name}-jar" m2compatible="true" root="{url}" pattern="[organization]/[module]/[revision]/[module]-[revision].[ext]" />
"""
        f.write(data)

    chainCommon = """
        <chain name="public-chain" returnFirst="true">
                <resolver ref="mavenorg-aar"/>
                <resolver ref="mavenorg-jar"/>
                <resolver ref="google-android-aar"/>
                <resolver ref="google-android-jar"/>
"""
    f.write(chainCommon)
    for line in lines:
        name = line.strip().split(',')[0]
        chainInternal = f"""
                <resolver ref="{name}-aar"/>
                <resolver ref="{name}-jar"/>
"""
        f.write(chainInternal)

    chainClose = """</chain>"""
    f.write(chainClose)

    footer = """
    </resolvers>
</ivysettings>"""
    f.write(footer)
