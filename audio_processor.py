import subprocess
def make_hardtekk(inp,out):
    cmd=[
    "ffmpeg","-y","-i",inp,
    "-filter:a",
    "asetrate=44100*1.1,atempo=1.15,bass=g=8,equalizer=f=1000:t=q:w=1:g=3,acompressor",
    out]
    subprocess.run(cmd,check=True)
