"""Embedding File

Will be a raw format file for storing the embeddings for the cocument text

BEGIN META


{
    JSON formatted meta data to simplify life
}


END META


BEGIN EMBEDDING

XXXXXXXXXX -Whatever the embedding data is

END EMBEDDING

BEGIN PAYLOAD

xxxxxx - whatever raw text we want to store

END PAYLOAD


BEGIN EMBEDDING

XXXXXXXXXX -Whatever the embedding data is

END EMBEDDING

BEGIN PAYLOAD

xxxxxx - whatever raw text we want to store

END PAYLOAD

.... These two sections repeat over and over again

"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple


class EmbeddingIOFile:
    def __init__(self, file_location: Path, metadata: Dict[str, Any]) -> None:
        """Create a new EmbeddingIOFile object

        Args:
            file_location (Path): Path to the file
            metadata (Dict[str, Any]): Metadata to be stored in the file
        """
        self.file_location: Optional[Path] = file_location
        self.file_pointer = open(file_location, "w")
        self.file_pointer.write("\n\n\n\nBEGIN META\n\n\n\n")
        self.file_pointer.write(json.dumps(metadata))
        self.file_pointer.write("\n\n\n\nEND META\n\n\n\n")
        self.file_pointer.close()

        # self._write_jobs: List[str] = []

        # Spin up a worker thread to keep writing in the data

    def write_text_data(self, embedding: List[float], text: str) -> None:
        """Write the embedding and the text to the file

        Args:
            embedding (List[float]): Embedding Vector
            text (str): Text data
        """
        if self.file_location is not None:
            self.file_pointer = open(self.file_location, "a")
        else:
            raise ValueError("File location cannot be None")
        self.file_pointer.write("\n\n\n\nBEGIN EMBEDDING\n\n\n\n")
        self.file_pointer.write(str(embedding))
        self.file_pointer.write("\n\n\n\nEND EMBEDDING\n\n\n\n")
        self.file_pointer.write("\n\n\n\nBEGIN PAYLOAD\n\n\n\n")
        self.file_pointer.write(text)
        self.file_pointer.write("\n\n\n\nEND PAYLOAD\n\n\n\n")
        self.file_pointer.close()

    @staticmethod
    def dump(
        file_location: Path,
        metadata: Dict[str, Any],
        embeddings: List[Tuple[List[float], str]],
    ) -> None:
        """Write the metadata and the embeddings to the file

        Args:
            file_location (Path): Location of the embedding file
            metadata (Dict[str,Any]): Metadata to be stored in the file
            embeddings (List[Tuple[List[float], str]]): List of tuples containing the embedding and the text data
        """

        eiofile = EmbeddingIOFile(file_location=file_location, metadata=metadata)

        for embedding, payload in embeddings:
            eiofile.write_text_data(embedding, payload)

    @staticmethod
    def parse(file_path: Path) -> Tuple[Dict[str, Any], List[Tuple[List[float], str]]]:
        """Parse the embedding file and return the metadata and the embeddings

        Args:
            file_path (Path): Path to the embedding file

        Returns:
            Tuple[Dict[str, Any], List[Tuple[List[float], str]]]: Metadata and the embeddings
        """
        # Read file line by line
        # Regex match check if line is new line or whitespaces + newline, skip
        # Check for regex matching for the different section HEADERs (BEGIN ????)
        # Keep a buffer (key value pair inticating the type of data defined by the header) to keep the text until you see the section FOOTER (END ??)
        # now once you hit the footer, you read the data in the buffer as follows:
        # META - Create a json object
        # EMBEDDING - Parse it into a float
        # PAYLOAD - add a new key value pair to the return dict

        ret_meta_dict: Dict[str, Any] = {}

        ret_embedding_list: List[Tuple[List[float], str]] = []

        parse_buffer = {"META": "", "EMBEDDING": "", "PAYLOAD": ""}

        EMPTY_LINE_REGEX = re.compile(r"\s*$")

        SECTION_REGEX_START = re.compile(r"\s*BEGIN\s+(\w+)\s*")

        SECTION_REGEX_END = re.compile(r"\s*END\s+(\w+)\s*")

        current_section_type = ""  # Will be META/EMBEDDING/PAYLOAD

        current_embedding = []
        current_payload = ""

        with open(file_path, "r", encoding="utf-8") as file_ptr:
            line_text = file_ptr.readline()
            while line_text:
                if re.match(EMPTY_LINE_REGEX, line_text):
                    line_text = file_ptr.readline()
                    continue

                section_begin_test = re.match(SECTION_REGEX_START, line_text)
                if section_begin_test:
                    # Figure out what kind
                    current_section_type = section_begin_test.group(1)
                    # Reset the corresponding parse buffers
                    parse_buffer[current_section_type] = ""
                    line_text = file_ptr.readline()
                    continue

                section_end_test = re.match(SECTION_REGEX_END, line_text)
                if section_end_test:
                    # Load up the data based on the type
                    if current_section_type == "META":
                        # Load up the json
                        ret_meta_dict = json.loads(parse_buffer["META"])

                    elif current_section_type == "EMBEDDING":
                        # Parse the string to a list of floats and set it to the kvp
                        float_string = parse_buffer["EMBEDDING"]
                        float_string = float_string.strip()

                        values_list = float_string[1:-1].split(",")
                        float_list = [float(value) for value in values_list]

                        # current_key_value_pair[0] = float_list
                        current_embedding = float_list

                    elif current_section_type == "PAYLOAD":
                        # Load the kvp with the payload as is
                        # current_key_value_pair[1] = parse_buffer["PAYLOAD"]
                        current_payload = parse_buffer["PAYLOAD"]

                        # Add to the return dict
                        ret_embedding_list.append((current_embedding, current_payload))

                    line_text = file_ptr.readline()
                    continue

                # If we reach here, just append to the parse buffer
                parse_buffer[current_section_type] += line_text

                line_text = file_ptr.readline()

        return ret_meta_dict, ret_embedding_list
