import json
import os
import unittest
from unittest.mock import patch, Mock
from script import extract_trace_id
from script import fetch_trace_data

# Pruebas unitarias
class TestExtractTraceId(unittest.TestCase):

    def test_valid_url(self):
        url = "https://example.com/traces/abc123def456"
        self.assertEqual(extract_trace_id(url), "abc123def456")

    def test_valid_url_with_other_paths(self):
        url = "https://example.com/some/other/path/traces/abc123def456/more/path"
        self.assertEqual(extract_trace_id(url), "abc123def456")

    def test_url_without_trace_id(self):
        url = "https://example.com/no/trace/here"
        self.assertIsNone(extract_trace_id(url))

    def test_url_with_invalid_trace_id(self):
        url = "https://example.com/traces/invalid_trace_id"
        self.assertIsNone(extract_trace_id(url))

    def test_url_with_multiple_trace_ids(self):
        url = "https://example.com/traces/abc123/traces/def456"
        self.assertEqual(extract_trace_id(url), "abc123")

    def test_url_with_trace_id_at_end(self):
        url = "https://example.com/traces/abc123"
        self.assertEqual(extract_trace_id(url), "abc123")

    def test_url_with_trace_id_at_start(self):
        url = "/traces/abc123/more/path"
        self.assertEqual(extract_trace_id(url), "abc123")

    def test_url_with_trace_id_and_query_params(self):
        url = "https://example.com/traces/abc123?param=value"
        self.assertEqual(extract_trace_id(url), "abc123")

    def test_url_with_trace_id_and_fragment(self):
        url = "https://example.com/traces/abc123#section"
        self.assertEqual(extract_trace_id(url), "abc123")

    def test_url_with_trace_id_query_params_and_fragment(self):
        url = "https://example.com/traces/abc123?param=value#section"
        self.assertEqual(extract_trace_id(url), "abc123")


class TestFetchTraceData(unittest.TestCase):
    @patch("requests.get")
    def test_fetch_trace_data_success(self, mock_get):
        # Configurar el mock para simular una respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"trace_id": "abc1234", "data": "example"}
        mock_get.return_value = mock_response

        # Llamar a la función
        base_url = "https://example.com"
        trace_id = "abc1234"
        save_path = "test_output/trace_data.json"
        result = fetch_trace_data(base_url, trace_id, save_path)

        # Verificar que la función devuelve True
        self.assertIsNotNone(result)

        # Verificar que el archivo se creó y contiene los datos correctos
        with open(save_path, "r") as file:
            saved_data = json.load(file)
        self.assertEqual(saved_data, {"trace_id": "abc1234", "data": "example"})

        # Limpiar: eliminar el archivo creado
        os.remove(save_path)

    @patch("requests.get")
    def test_fetch_trace_data_failure(self, mock_get):
        # Configurar el mock para simular una respuesta fallida
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Llamar a la función
        base_url = "https://example.com"
        trace_id = "invalid_trace"
        save_path = "test_output/trace_data.json"
        result = fetch_trace_data(base_url, trace_id, save_path)

        # Verificar que la función devuelve False
        self.assertIsNone(result)

        # Verificar que el archivo no se creó
        self.assertFalse(os.path.exists(save_path))

if __name__ == "__main__":
    unittest.main()