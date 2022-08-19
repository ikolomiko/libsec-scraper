#!/usr/bin/env python3

lines = []
with open("repo_stats.csv", 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open("ivy-public.xml", 'w', encoding='utf-8') as f:
    header = """<ivysettings>
             <resolvers>"""
    f.write(header)

    chainCommon = """<chain name="public-chain" returnFirst="true">
                <resolver ref="mavenorg-aar"/>
                <resolver ref="public"/>
                <resolver ref="google-android-aar"/>
                <resolver ref="google-android-jar"/>"""
    f.write(chainCommon)
    for line in lines:
        name = line.strip().split(',')[0]
        chainInternal = f""" <resolver ref="{name}-aar"/>
                        <resolver ref="{name}-jar"/>
                        """
        f.write(chainInternal)

    chainClose = """</chain>"""
    f.write(chainClose)

    addition = """<url name="google-android-aar" m2compatible="true">
            <artifact pattern="https://dl.google.com/dl/android/maven2/[organization]/[module]/[revision]/[module]-[revision].aar"/>
        </url>
        <url name="google-android-jar" m2compatible="true">
            <artifact pattern="https://dl.google.com/dl/android/maven2/[organization]/[module]/[revision]/[module]-[revision].jar"/>
        </url>
        <url name="mavenorg-aar" m2compatible="true">
            <artifact pattern="https://repo1.maven.org/maven2/[organization]/[module]/[revision]/[module]-[revision].aar"/>
        </url>
        <ibiblio name="public" m2compatible="true"/>"""
    f.write(addition)

    for line in lines:
        (name, usages, url) = line.strip().split(',')
        data = f"""<url name="{name}-aar" m2compatible="true">
                           <artifact pattern="{url}/[organization]/[module]/[revision]/[module]-[revision].aar"/>
                       </url>
                       <url name="{name}-jar" m2compatible="true">
                           <artifact pattern="{url}/[organization]/[module]/[revision]/[module]-[revision].jar"/>
                       </url>"""
        f.write(data)

    footer = """</resolvers>
    </ivysettings>"""
    f.write(footer)
