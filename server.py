from mcpi import minecraft
import time
import mcpi.block as block

mc = minecraft.Minecraft.create(address="127.0.0.1", name="steve")

servers = [
    {
        'server': mc,
        'opts': {
            'bow': '',
            'sword': ''
        }
    }
]

POSITIVE_X = "x"
NEGATIVE_X = "-x"
POSITIVE_Z = "z"
NEGATIVE_Z = "-z"

def getPlayerFacing(server):
    direction = server.player.getRotation() * -1

    if 45 < direction < 135:
        return POSITIVE_X
    elif 135 < direction < 225:
        return NEGATIVE_Z
    elif 225 < direction < 315:
        return NEGATIVE_X
    else:
        return POSITIVE_Z

def getBlockId(block_type, server):
    try:
        return getattr(block, block_type.upper()).id
    except AttributeError:
        server.postToChat("No block type: %(block_type)s found" % locals())

def build_rect(distance, height, length, block_type, server):
    print distance, height, length
    print block_type

    player_facing = getPlayerFacing(server)
    player_pos = server.player.getPos()

    # both start at 0 offset
    x_offset = z_offset = 0
    start_x = start_z = 0 # push one block forward so we don't build outselves inside a wall
    z_width = x_width = 0

    if player_facing == POSITIVE_X:
        x_offset = distance
        start_x = 1
        z_width = length
    elif player_facing == NEGATIVE_Z:
        z_offset = -distance
        start_z = -1
        x_width = length
    elif player_facing == NEGATIVE_X:
        x_offset = -distance
        start_x = -1
        z_width = -length
    elif player_facing == POSITIVE_Z:
        z_offset = distance
        start_z = 1
        x_width = -length
    else:
        print "I have no idea what happened."

    try:
        server.setBlocks(
            player_pos.x + start_x,
            player_pos.y,
            player_pos.z + start_z,
            player_pos.x + x_offset + x_width,
            player_pos.y + height,
            player_pos.z + z_offset + z_width,
            getBlockId(block_type)
        )
    except AttributeError:
        server.postToChat("No block type: %(block_type)s found" % locals())

while True:
    for server_and_opts in servers:
        server = server_and_opts['server']
        opts = server_and_opts['opts']

        for chatpost in server.player.pollChatPosts():
            message = chatpost.message.lower()
            if message == "help":
                server.postToChat("The following options exist:")
                server.postToChat("teleport ( on | off )")
                server.postToChat("redstone tnt ( on | off )")
                server.postToChat("RECT (LENGTH) (HEIGHT) (WIDTH) (BLOCK_TYPE)")
                server.postToChat("WALL (LENGTH) (HEIGHT) (BLOCK_TYPE)")
                server.postToChat("BOW (BLOCK_TYPE)")
            elif message == "teleport on":
                opts['bow'] = 'teleport'
                server.postToChat('Teleport activated!')
            elif message == "teleport off":
                opts['bow'] = ''
                server.postToChat('Teleport deactivated!')
            elif message == "redstone tnt on":
                opts['sword'] = 'redstone_tnt'
                server.postToChat('Redstone TNT activated!')
            elif message == "redstone tnt off":
                opts['sword'] = ''
                server.postToChat('Redstone TNT deactivated!')
            elif "bow" in message:
                block_type = message.split()[1]
                opts['bow'] = getBlockId(block_type, server)
                print opts
            elif "wall" in message:
                message_tokens = message.split()
                distance = int(message_tokens[1])
                height = int(message_tokens[2]) - 1
                block_type = message_tokens[3]

                build_rect(distance, height, 0, block_type, server)

            elif "rect" in message:
                message_tokens = message.split()
                distance = int(message_tokens[1])
                height = int(message_tokens[2]) - 1
                length = int(message_tokens[3]) - 1
                block_type = message_tokens[4]

                build_rect(distance, height, length, block_type, server)


        for blockhit in server.player.pollProjectileHits():
            if opts['bow'] == 'teleport':
                pos = blockhit.pos
                server.player.setPos(pos.x, pos.y, pos.z)
            elif isinstance(opts['bow'], int):
                pos = blockhit.pos
                server.setBlocks(pos.x, pos.y, pos.z, pos.x, pos.y, pos.z, opts['bow'])

        for blockhit in server.player.pollBlockHits():
            if opts['sword'] == 'redstone_tnt':
                pos = blockhit.pos
                server.setBlocks(pos.x, pos.y, pos.z, pos.x, pos.y, pos.z, 152)
                server.setBlocks(pos.x, pos.y+1, pos.z, pos.x, pos.y+1, pos.z, 46)

    time.sleep(1)
