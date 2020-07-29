<?php

/**
 * Copyright (c) 2019 Nadav Tasher
 * https://github.com/NadavTasher/Template/
 **/

/**
 * Base API for storing user data.
 */
class Keystore
{
    // Constants
    public const API = "keystore";

    // Keystore name
    private string $name;

    /**
     * Keystore constructor.
     * @param string $name Name
     */
    public function __construct($name)
    {
        $this->name = $name;
    }

    /**
     * Inserts a new entry to the keystore.
     * @param string | null $id Entry ID
     * @return string Entry ID
     */
    public function insert($id = null)
    {
        // Generate a row ID
        if ($id === null) {
            $id = Base::random(10);
        }
        // Make sure the entry does not exist
        if ($this->exists($id))
            throw new Error("Entry already exists");
        // Create entry path
        $path = self::path($id);
        // Create the directory
        mkdir($path);
        // Return the ID
        return $id;
    }

    /**
     * Removes an entry from the keystore.
     * @param string $id Entry ID
     */
    public function remove($id)
    {
        // Make sure the entry exists
        if (!$this->exists($id))
            throw new Error("Entry does not exist");
        // Create entry path
        $path = self::path($id);
        // Scan entry directory
        $values = scandir($path);
        $values = array_slice($values, 2);
        // Remove all values
        foreach ($values as $value) {
            unlink(Base::path($value, $path));
        }
        // Remove the directory
        rmdir($path);
    }

    /**
     * Checks whether a keystore entry exists.
     * @param string $id Entry ID
     * @return bool
     */
    public function exists($id)
    {
        // Create entry path
        $path = self::path($id);
        // Check existence
        return file_exists($path) && is_dir($path);
    }

    /**
     * Sets a keystore value.
     * @param string $id Entry ID
     * @param string $key Key
     * @param mixed $value Value
     */
    public function set($id, $key, $value)
    {
        // Make sure the entry exists
        if (!$this->exists($id))
            throw new Error("Entry does not exist");
        // Create path
        $path = self::path($id, $key);
        // Check if value is null
        if ($value === null) {
            // Make sure the path exists
            if ($this->get($id, $key) !== null) {
                // Remove the value
                unlink($path);
            }
        } else {
            // Update the value
            file_put_contents($path, json_encode($value));
        }
    }

    /**
     * Gets a keystore value.
     * @param string $id Entry ID
     * @param string $key Key
     * @return mixed Value
     */
    public function get($id, $key)
    {
        // Make sure the entry exists
        if (!$this->exists($id))
            throw new Error("Entry does not exist");
        // Create path
        $path = self::path($id, $key);
        // Make sure the value path exists
        if (file_exists($path) && is_file($path)) {
            // Read and return value
            return json_decode(file_get_contents($path));
        } else {
            return null;
        }
    }

    /**
     * Searches through the keystore for matches.
     * @param string $key Key
     * @param mixed $value Value
     * @return array Results
     */
    public function search($key, $value)
    {
        // Initialize the results array
        $array = array();
        // Create path
        $path = self::path();
        // Scan entries
        $ids = scandir($path);
        $ids = array_slice($ids, 2);
        // Search for matches
        foreach ($ids as $id) {
            // Check value match
            if ($value === $this->get($id, $key)) {
                array_push($array, $id);
            }
        }
        // Return success
        return $array;
    }

    /**
     * Creates a keystore path.
     * @param string | null $id Entry ID
     * @param string | null $key Key
     * @return string Path
     */
    private function path($id = null, $key = null)
    {
        // Check if id is null
        if ($id === null)
            return Base::file("$this->name", self::API);;
        // Hex encode id
        $id = bin2hex($id);
        // Check if key is null
        if ($key === null)
            return Base::file("$this->name:$id", self::API);;
        // Hex encode key
        $key = bin2hex($key);
        // Create path with key
        return Base::file("$this->name:$id:$key", self::API);
    }
}