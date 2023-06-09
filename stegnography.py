# Convert data to 8-bit binary form
def data2Bin(data):
    if type(data) == str:
        return ''.join((format(ord(i), '08b') for i in data))
    elif type(data) == tuple:
        return tuple(format(i, '08b') for i in data)


def encode(img, msg):
    print("Encoding process started....")
    print(f"Image length: {len(img)}, Message Length: {len(msg)}")
    try:
        if len(msg) > len(img) - 1:
            raise ValueError("Need a large image!")
        msg = data2Bin(chr(247)+msg+chr(248))
        # Splitting the data into an 8-bit form
        msg_set = [msg[i: i + 8] for i in range(0, len(msg), 8)]
        # Randomly taken all the pixel index values based on the given password
        try:
            # Adding message to given image
            img = list(img)
            for i, val in enumerate(msg_set):
                im_data = list(data2Bin(img[i]))
                t_data = []
                red, green, blue = im_data[0][:5], im_data[1][:5], im_data[2][:6]
                msg_grp1, msg_grp2, msg_grp3 = val[0:3], val[3:6], val[6:8]
                # Adding 3-bit to red
                t_data.append(int(red + msg_grp1, 2))
                # Adding 3-bit to green
                t_data.append(int(green + msg_grp2, 2))
                # Adding 2-bit to blue
                t_data.append(int(blue + msg_grp3, 2))
                img[i] = tuple(t_data)
            print("Encoding process finished!")
            return img

        # Checking the image is suitable for storing the message (message is in 8-bit form)
        except Exception as ex:
            print("Encoding process halted!")
            print(f"Error: {ex}")
            return f"{ex}"

    except Exception as ex:
        print(ex)


def decode(img):
    start =True
    print("Decoding process started....")
    try:
        img = list(img)
        catstr = ''
        for i, val in enumerate(img):
            im_data = list(data2Bin(img[i]))
            msg_grp1, msg_grp2, msg_grp3 = im_data[0][5:], im_data[1][5:], im_data[2][6:]
            t_str = chr(int(msg_grp1 + msg_grp2 + msg_grp3, 2))
            if t_str != chr(247) and start:
                return chr(247)
            if t_str == chr(248):
                break
            start = False
            catstr += t_str
        print("Decoding process finished....")
        return catstr[1:]
    except Exception as ex:
        print("Decoding process halted!")
        print(f"Error: {ex}")
        return chr(247)
