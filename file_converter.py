import numpy as np
import re

class FileConverter:

    def parse_file(self, filename):
        with open(filename+".txt", 'r') as textfile:
            text = textfile.read()
            bio = np.chararray(len(text), itemsize=1)
            bio[:] = "O"
            type = np.chararray(len(text), itemsize=2)
            type[:] = "X"
            distance = np.empty(len(text))
            distance[:] = np.nan
            stance = np.chararray(len(text), itemsize=4)
            stance[:] = "X"

        with open(filename+".ann", 'r') as annfile:
            entitiesDict = {}
            for line in annfile:
                components = line.split()
                if components[1] in ["MajorClaim", "Claim", "Premise"]:
                    entitiesDict[components[0]] = [int(components[2]), int(components[3])]
                    bio[int(components[2]):int(components[3])] = "I"
                    bio[int(components[2])] = "B"
                    if components[1] == "MajorClaim":
                        type[int(components[2]):int(components[3])] = "MC"
                    elif components[1] == "Claim":
                        type[int(components[2]):int(components[3])] = "C"
                    elif components[1] == "Premise":
                        type[int(components[2]):int(components[3])] = "P"
                elif components[1] in ["supports", "attacks"]:
                    arg1 = components[2].split(":")
                    arg2 = components[3].split(":")
                    if arg1[0] != "Arg1" or arg2[0] != "Arg2":
                        raise ValueError("Arg1 and Arg2 are not in correct order. File: "+filename+" At "+components[0])

                    dist = int(arg2[1][1:]) - int(arg1[1][1:])
                    distance[entitiesDict[arg1[1]][0]:entitiesDict[arg1[1]][1]] = dist
                    if components[1] == "supports":
                        stance[entitiesDict[arg1[1]][0]:entitiesDict[arg1[1]][1]] = "Supp"
                    elif components[1] == "attacks":
                        stance[entitiesDict[arg1[1]][0]:entitiesDict[arg1[1]][1]] = "Att"
                elif components[1] == "Stance":
                    stance[entitiesDict[components[2]][0]:entitiesDict[components[2]][1]] = components[3]
                else:
                    raise ValueError("Unexpected input "+components[1]+". File: "+filename+" At "+components[0])

        output = []

        for m in re.finditer(r'\S+', text):
            index, item = m.start(), m.group()
            startIdx = index
            endIdx = index + len(item)
            additionalIdx = -1
            if item[-1] in [".", ",", ";", ":", "?", "!"]:
                endIdx = index + len(item) - 1
                additionalIdx = index + len(item) - 1

            # if np.any(bio[startIdx:endIdx] != bio[startIdx]) and (bio[startIdx] != b"B" or np.any(bio[startIdx+1:endIdx] != b"I")):
            #     raise ValueError("BIO array is not correct in File: "+filename)
            #
            # if np.any(type[startIdx:endIdx] != type[startIdx]):
            #     raise ValueError("Type array is not correct in File: "+filename)
            #
            # if np.any(distance[startIdx:endIdx] != distance[startIdx]) and not np.all(np.isnan(distance[startIdx:endIdx])):
            #     raise ValueError("Distance array is not correct in File: "+filename)
            #
            # if np.any(stance[startIdx:endIdx] != stance[startIdx]):
            #     raise ValueError("Stance array is not correct in File: "+filename)

            if np.isnan(distance[startIdx]):
                dist = "X";
            else:
                dist = str(int(distance[startIdx]))
            output.append({'text': text[startIdx:endIdx], 'b': bio[startIdx], 't': type[startIdx],
                            'd': dist, 's': stance[startIdx]})

            if additionalIdx != -1:
                if np.isnan(distance[additionalIdx]):
                    dist = "X";
                else:
                    dist = int(distance[additionalIdx])
                output.append({'text': text[additionalIdx], 'b': bio[additionalIdx], 't': type[additionalIdx],
                                'd': dist, 's': stance[additionalIdx]})
        # for element in output:
        #     print(element)
        return output

# fc = FileConverter()
# data_dir = "../brat-project-final/"
# start_id = 1
# end_id = 402
#
# for i in range(start_id, end_id + 1):
#     filename = '{}essay{:03d}'.format(data_dir, i)
#     parsed_file = fc.parse_file(filename)
#     for element in parsed_file:
#         print(element)
